---
name: modal
description: >
  Run compute on Modal — GPUs, CPU swarms, web endpoints, scheduled jobs.
  Use when the user needs cloud compute, GPU inference, training, batch
  processing, or parallel workloads. Do NOT use for local-only tasks or
  when the user has not set up a Modal account.
allowed-tools: Bash(uv run *), Read, Write, Glob
---

Modal provides serverless containers with sub-5s cold starts. No SSH, no Kubernetes, no Docker registry. [Docs](https://modal.com/docs/guide) · [Examples](https://modal.com/docs/examples) · [API Reference](https://modal.com/docs/reference)

## First-Time Setup

### Prerequisites

- **Python 3.11+** and **[uv](https://docs.astral.sh/uv/getting-started/installation/)** installed
- **Modal package**: If using this skills repo, `make install` handles it. Standalone: `uv tool install modal`

### 1. Create a Modal Account

Sign up at [modal.com](https://modal.com). Go to **Settings → API Tokens** to create a token pair (token ID + secret).

### 2. Authenticate

**For humans** — token file (simplest):
```bash
uv run modal token set --token-id <ID> --token-secret <SECRET>
```
Writes to `~/.modal.toml`. Use `--profile <name>` for multiple accounts, then `modal profile activate <name>`.

**For agents and CI** — environment variables (takes precedence over token file):
Add to `~/.zshrc` (or `~/.bashrc`) so they're available when Claude Code launches:
```bash
export MODAL_TOKEN_ID="ak-..."
export MODAL_TOKEN_SECRET="as-..."
```
Then `source ~/.zshrc` or restart your terminal.

### 3. Verify

```bash
uv run --script SKILL_DIR/scripts/modal_helper.py check-auth
```

## CLI (always use `uv run modal`)

```bash
uv run modal run script.py                # run @app.local_entrypoint()
uv run modal run script.py --detach       # run in background (survives terminal close)
uv run modal serve script.py              # dev server with hot reload (web endpoints)
uv run modal deploy script.py             # persistent production deployment
uv run modal shell --gpu A100             # interactive GPU shell
uv run modal volume create my-data        # create volume
uv run modal volume put my-data ./local /remote
uv run modal volume get my-data /remote ./local
```

## GPU Options & Pricing

| GPU | VRAM | $/hr | Max per container | Best for |
|-----|------|------|-------------------|----------|
| `T4` | 16 GB | $0.59 | 8 | Light inference, prototyping |
| `L4` | 24 GB | $0.80 | 8 | Lightweight inference |
| `A10G` | 24 GB | $1.10 | 4 | Inference, moderate training |
| `L40S` | 48 GB | $1.95 | 8 | Vision, mid training |
| `A100` (40 GB) | 40 GB | $2.10 | 8 | Training, large inference |
| `A100` (80 GB) | 80 GB | $2.50 | 8 | 7B-70B models |
| `H100` | 80 GB | $3.95 | 8 | Large-scale training, best ecosystem support |
| `H200` | 141 GB | $4.54 | 8 (1,128 GB total) | Large models, 671B fits on 8x |
| `B200` | 192 GB | $6.25 | 8 (1,440 GB total) | Fastest; ~2.5x faster TTFT vs H200 |

Multi-GPU: `gpu="A100:4"`. GPU fallbacks: `gpu=["h100", "a100", "any"]`. CPU-only: omit `gpu=`.
[Pricing details](https://modal.com/pricing) · [GPU guide](https://modal.com/docs/guide/gpu)

## Patterns

### GPU function (simplest)

```python
import modal

app = modal.App("my-app")
image = modal.Image.debian_slim(python_version="3.12").uv_pip_install("torch")

@app.function(gpu="A100", image=image, timeout=3600)
def train():
    import torch
    print(f"CUDA: {torch.cuda.is_available()}, GPU: {torch.cuda.get_device_name(0)}")

@app.local_entrypoint()
def main():
    train.remote()
```

### Stateful service with model loading (`@app.cls`)

Use for GPU inference — load model once, serve many requests:

```python
import modal

app = modal.App("inference")
image = modal.Image.debian_slim(python_version="3.12").uv_pip_install("vllm")

@app.cls(gpu="H100", image=image)
@modal.concurrent(max_inputs=32)
class LLM:
    @modal.enter()
    def load(self):
        import vllm
        self.engine = vllm.LLM("meta-llama/Llama-3-8B")

    @modal.method()
    def generate(self, prompt: str) -> str:
        return self.engine.generate(prompt)[0].outputs[0].text

    @modal.exit()
    def cleanup(self):
        del self.engine
```

[Lifecycle hooks](https://modal.com/docs/guide/lifecycle-functions) · [Concurrency](https://modal.com/docs/guide/concurrent-inputs)

### Parallel map (CPU swarm or GPU fleet)

```python
@app.function(image=image)
def process(item: str) -> str:
    return f"processed: {item}"

@app.local_entrypoint()
def main():
    results = list(process.map(["a", "b", "c", "d"]))  # parallel, ordered
    print(results)
```

`.map()` for ordered results, `.for_each()` for fire-and-forget, `.starmap()` for multi-arg.
[Scaling out](https://modal.com/docs/guide/scale)

### Async spawn with gather

```python
@app.local_entrypoint()
def main():
    job_a = step1.spawn("foo")
    job_b = step2.spawn(42)
    results = modal.FunctionCall.gather(job_a, job_b)
```

`.spawn()` returns immediately. `.get()` blocks for result. `.spawn_map()` for async fan-out.

### Volumes for persistent storage

```python
vol = modal.Volume.from_name("my-data", create_if_missing=True)

@app.function(volumes={"/data": vol})
def save():
    Path("/data/output.txt").write_text("done")
    vol.commit()  # required for writes to be visible to other containers
```

[Volumes guide](https://modal.com/docs/guide/volumes)

### Web endpoint

```python
@app.function(gpu="A100", image=image)
@modal.fastapi_endpoint()
def predict(prompt: str):
    return {"result": "..."}
```

Deploy: `uv run modal deploy script.py` — returns a URL.
For full apps: `@modal.asgi_app()` (FastAPI), `@modal.wsgi_app()` (Flask/Django).
[Web endpoints](https://modal.com/docs/guide/webhooks)

### Scheduled function

```python
@app.function(schedule=modal.Cron("0 */6 * * *"))
def periodic_job():
    print("Runs every 6 hours")
```

Only active when deployed (`uv run modal deploy`). Also: `modal.Period(hours=1)`.
[Scheduling](https://modal.com/docs/guide/cron)

### Dynamic batching (high-throughput inference)

```python
@app.cls(gpu="H100", image=image)
class Embedder:
    @modal.enter()
    def load(self):
        self.model = load_model()

    @modal.batched(max_batch_size=64, wait_ms=1000)
    async def embed(self, texts: list[str]) -> list[list[float]]:
        return self.model.encode(texts).tolist()
```

Callers send single inputs; Modal accumulates into batches transparently.
[Dynamic batching](https://modal.com/docs/guide/dynamic-batching)

## Scaling Config

| Parameter | Purpose |
|-----------|---------|
| `max_containers` | Hard cap on container count |
| `min_containers` | Warm floor (prevents scale-to-zero; costs money when idle) |
| `buffer_containers` | Extra warm containers while function is active (burst handling) |
| `scaledown_window` | Seconds before idle container shuts down (default 60, max 1200) |
| `single_use_containers=True` | Fresh container per input (no reuse) |
| `timeout` | Max execution time per input (max 24h) |
| `retries` | Int or `modal.Retries(initial_delay=0.0, max_retries=10)` |

## Image Building

```python
image = (
    modal.Image.debian_slim(python_version="3.12")
    .apt_install("ffmpeg", "git")
    .uv_pip_install("torch==2.8.0", "transformers")  # pin versions
    .env({"MY_VAR": "value"})
    .add_local_python_source("my_package")        # replaces deprecated mount=
)
```

Also: `Image.from_registry(...)`, `Image.from_dockerfile(...)`, `Image.uv_sync()` for uv projects.
[Images guide](https://modal.com/docs/guide/images) · [Image reference](https://modal.com/docs/reference/modal.Image)

For advanced patterns (sandboxes, dicts/queues, secrets, 1.0 migration), see [reference.md](reference.md).

## Troubleshooting

- **Auth failed**: Run `uv run modal token set` or set `MODAL_TOKEN_ID` + `MODAL_TOKEN_SECRET`
- **OOM on GPU**: Use a larger GPU or reduce batch size
- **Timeout**: Increase `timeout=` (default 300s, max 24h). Use `--detach` for long jobs
- **Import errors in container**: Add packages to `.uv_pip_install()` in the image definition
- **Cold starts slow**: Use `min_containers`, or bake model into image with `Image.run_function()`
