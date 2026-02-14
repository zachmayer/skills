#!/usr/bin/env python3
"""Helper utilities for the Modal compute skill."""

import os
import subprocess

import click


def _run_modal(args: list[str], capture: bool = True) -> subprocess.CompletedProcess[str]:
    """Run a modal CLI command."""
    return subprocess.run(
        ["modal", *args],
        capture_output=capture,
        text=True,
    )


@click.group()
def cli() -> None:
    """Modal compute skill helpers."""


@cli.command()
def check_auth() -> None:
    """Check if Modal authentication is configured and working."""
    token_id = os.environ.get("MODAL_TOKEN_ID")
    token_secret = os.environ.get("MODAL_TOKEN_SECRET")

    if token_id and token_secret:
        click.echo("Environment: MODAL_TOKEN_ID and MODAL_TOKEN_SECRET are set.")
    else:
        click.echo("Environment: MODAL_TOKEN_ID / MODAL_TOKEN_SECRET not set (may use token file).")

    # Test by listing apps — this validates the token
    result = _run_modal(["app", "list"])
    if result.returncode == 0:
        click.echo("Auth: OK — Modal CLI authenticated successfully.")
    else:
        stderr = result.stderr.strip()
        click.echo(f"Auth: FAILED — {stderr}", err=True)
        click.echo("", err=True)
        click.echo("To authenticate, either:", err=True)
        click.echo("  1. Run: modal token set", err=True)
        click.echo("  2. Set env vars in ~/.zshrc:", err=True)
        click.echo('     export MODAL_TOKEN_ID="your-token-id"', err=True)
        click.echo('     export MODAL_TOKEN_SECRET="your-token-secret"', err=True)
        raise SystemExit(1)


@cli.command()
@click.option("--name", "-n", required=True, help="App name (used for Modal app and filename)")
@click.option("--gpu", "-g", default=None, help="GPU type (e.g. A100, H100, T4, L40S, A100:4)")
@click.option("--pip", "-p", multiple=True, help="Pip packages to install (repeatable)")
@click.option(
    "--volume",
    "-v",
    default=None,
    help="Volume in name:/mount/path format (e.g. my-data:/mnt/data)",
)
@click.option(
    "--timeout",
    "-t",
    default=3600,
    type=int,
    help="Function timeout in seconds (default: 3600)",
)
@click.option(
    "--output",
    "-o",
    default=None,
    help="Output file path (default: ./<name>_modal.py)",
)
def scaffold(
    name: str,
    gpu: str | None,
    pip: tuple[str, ...],
    volume: str | None,
    timeout: int,
    output: str | None,
) -> None:
    """Generate a Modal app template file."""
    output_path = output or f"{name}_modal.py"

    # Build image section
    image_lines = []
    python_version = "3.11"
    if pip:
        pkg_str = ", ".join(f'"{p}"' for p in pip)
        image_lines.append(
            f'image = modal.Image.debian_slim(python_version="{python_version}")'
            f".pip_install({pkg_str})"
        )
    else:
        image_lines.append(f'image = modal.Image.debian_slim(python_version="{python_version}")')

    # Build volume section
    volume_lines = []
    volume_mount = ""
    if volume:
        parts = volume.split(":")
        if len(parts) != 2:
            click.echo("Error: --volume must be in name:/mount/path format", err=True)
            raise SystemExit(1)
        vol_name, mount_path = parts
        volume_lines.append(
            f'volume = modal.Volume.from_name("{vol_name}", create_if_missing=True)'
        )
        volume_mount = f', volumes={{"{mount_path}": volume}}'

    # Build function decorator
    decorator_parts = []
    if gpu:
        decorator_parts.append(f'gpu="{gpu}"')
    decorator_parts.append("image=image")
    decorator_parts.append(f"timeout={timeout}")
    if volume_mount:
        vol_name, mount_path = volume.split(":")
        decorator_parts.append(f'volumes={{"{mount_path}": volume}}')
    decorator = ", ".join(decorator_parts)

    # Assemble the file
    lines = ["import modal", ""]
    lines.append(f'app = modal.App("{name}")')
    lines.append(image_lines[0])
    if volume_lines:
        lines.append(volume_lines[0])
    lines.append("")
    lines.append("")
    lines.append(f"@app.function({decorator})")
    lines.append("def run():")
    lines.append('    """Your compute function. Edit this."""')
    if gpu:
        lines.append("    import torch")
        lines.append('    print(f"CUDA available: {torch.cuda.is_available()}")')
        if volume:
            _, mount_path = volume.split(":")
            lines.append("    import os")
            lines.append(f"    print(f\"Volume files: {{os.listdir('{mount_path}')}}\")")
    else:
        lines.append('    print("Hello from Modal!")')
        if volume:
            _, mount_path = volume.split(":")
            lines.append("    import os")
            lines.append(f"    print(f\"Volume files: {{os.listdir('{mount_path}')}}\")")
    lines.append("")
    lines.append("")
    lines.append("@app.local_entrypoint()")
    lines.append("def main():")
    lines.append("    run.remote()")

    content = "\n".join(lines) + "\n"

    with open(output_path, "w") as f:
        f.write(content)

    click.echo(f"Generated: {output_path}")
    click.echo("")
    click.echo("Next steps:")
    click.echo(f"  1. Edit {output_path} with your compute logic")
    click.echo(f"  2. Run: modal run {output_path}")
    if volume:
        vol_name, _ = volume.split(":")
        click.echo(f"  3. Check volume: modal volume ls {vol_name}")


if __name__ == "__main__":
    cli()
