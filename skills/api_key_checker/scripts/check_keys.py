"""Check which AI provider API keys are configured and valid."""

import os

import click
import httpx

PROVIDERS = {
    "OpenAI": {
        "env_var": "OPENAI_API_KEY",
        "url": "https://api.openai.com/v1/models",
        "auth_header": "Authorization",
        "auth_prefix": "Bearer ",
    },
    "Anthropic": {
        "env_var": "ANTHROPIC_API_KEY",
        "url": "https://api.anthropic.com/v1/messages",
        "auth_header": "x-api-key",
        "auth_prefix": "",
        "extra_headers": {"anthropic-version": "2023-06-01"},
    },
    "Google": {
        "env_var": "GOOGLE_API_KEY",
        "url": "https://generativelanguage.googleapis.com/v1beta/models",
        "auth_via_param": True,
        "param_name": "key",
    },
}


def check_provider(name: str, config: dict) -> dict:
    """Check if a provider's API key is configured and valid."""
    env_var = config["env_var"]
    key = os.environ.get(env_var, "").strip()

    if not key:
        return {"status": "missing", "env_var": env_var}

    # Mask key for display
    masked = key[:8] + "..." + key[-4:] if len(key) > 12 else "***"

    try:
        headers = {}
        params = {}

        if config.get("auth_via_param"):
            params[config["param_name"]] = key
        else:
            headers[config["auth_header"]] = config["auth_prefix"] + key

        if "extra_headers" in config:
            headers.update(config["extra_headers"])

        # Use GET for list endpoints, short timeout
        resp = httpx.get(config["url"], headers=headers, params=params, timeout=10.0)

        # Anthropic returns 405 on GET to /messages — that's fine, it means auth worked
        if resp.status_code in (200, 405):
            return {"status": "valid", "env_var": env_var, "key": masked}

        if resp.status_code in (401, 403):
            return {
                "status": "invalid",
                "env_var": env_var,
                "key": masked,
                "error": f"HTTP {resp.status_code}",
            }

        return {
            "status": "unknown",
            "env_var": env_var,
            "key": masked,
            "error": f"HTTP {resp.status_code}",
        }

    except httpx.TimeoutException:
        return {"status": "timeout", "env_var": env_var, "key": masked}
    except httpx.ConnectError as e:
        return {"status": "error", "env_var": env_var, "key": masked, "error": str(e)}


@click.command()
def main() -> None:
    """Check which AI provider API keys are configured and valid."""
    results = {}
    for name, config in PROVIDERS.items():
        results[name] = check_provider(name, config)

    click.echo("API Key Status:")
    for name, result in results.items():
        status = result["status"]
        env_var = result["env_var"]

        if status == "missing":
            click.echo(f"  {name:12s}  MISSING   ${env_var} not set")
        elif status == "valid":
            click.echo(f"  {name:12s}  OK        ${env_var} = {result['key']}")
        elif status == "invalid":
            click.echo(f"  {name:12s}  INVALID   ${env_var} = {result['key']}  ({result['error']})")
        elif status == "timeout":
            click.echo(
                f"  {name:12s}  TIMEOUT   ${env_var} = {result['key']}  (endpoint unreachable)"
            )
        else:
            click.echo(
                f"  {name:12s}  ERROR     ${env_var} = {result['key']}  ({result.get('error', 'unknown')})"
            )

    # Summary
    valid = sum(1 for r in results.values() if r["status"] == "valid")
    total = len(results)
    click.echo(f"\n{valid}/{total} providers configured and valid.")


if __name__ == "__main__":
    main()
