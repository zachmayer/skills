---
name: modal
description: >
  Run compute on Modal — GPUs, CPU swarms, persistent volumes.
  Use when the user needs cloud compute, GPU inference, training,
  batch processing, or parallel workloads. Do NOT use for local-only
  tasks or when the user has not set up a Modal account.
allowed-tools: Bash(uv run *), Bash(modal *), Read, Write, Glob
---

Modal provides serverless containers with sub-5s cold starts. No SSH, no Kubernetes, no Docker registry.

## Prerequisites

1. **Modal account**: Sign up at https://modal.com/
2. **Modal token**: Run `modal token set` or set env vars:
   ```bash
   export MODAL_TOKEN_ID="your-token-id"
   export MODAL_TOKEN_SECRET="your-token-secret"
   ```
3. **Check auth**: `uv run --script SKILL_DIR/scripts/modal_helper.py check-auth`

## CLI Quick Reference

```bash
modal run script.py                     # run @app.local_entrypoint()
modal shell --gpu A100                  # interactive GPU shell
modal deploy script.py                  # persistent deployment
modal volume create my-data             # create volume
modal volume put my-data ./local /remote  # upload
modal volume get my-data /remote ./local  # download
```

## GPU Options

| GPU | VRAM | Best for |
|-----|------|----------|
| `T4` | 16 GB | Light inference, prototyping |
| `L4` | 24 GB | Inference, small fine-tuning |
| `A10G` | 24 GB | Inference, moderate training |
| `A100` | 40/80 GB | Training, large inference |
| `H100` | 80 GB | Large-scale training |

Multi-GPU: `gpu="A100:4"` for 4x GPUs. CPU-only: omit the `gpu=` parameter.

## Patterns

Write Modal apps directly — no scaffold needed. Use these patterns as building blocks.

### GPU function

```python
import modal

app = modal.App("my-app")
image = modal.Image.debian_slim(python_version="3.11").pip_install("torch")

@app.function(gpu="A100", image=image, timeout=3600)
def train():
    import torch
    print(f"CUDA: {torch.cuda.is_available()}, Device: {torch.cuda.get_device_name(0)}")

@app.local_entrypoint()
def main():
    train.remote()
```

### Persistent storage with volumes

```python
import modal

app = modal.App("data-app")
volume = modal.Volume.from_name("my-data", create_if_missing=True)

@app.function(volumes={"/mnt/data": volume}, timeout=3600)
def process():
    import os
    print(f"Files: {os.listdir('/mnt/data')}")
    with open("/mnt/data/output.txt", "w") as f:
        f.write("done")

@app.local_entrypoint()
def main():
    process.remote()
```

### Parallel map (CPU swarm or GPU fleet)

```python
@app.function(gpu="T4", image=image)
def process_item(item: str) -> str:
    return f"processed: {item}"

@app.local_entrypoint()
def main():
    results = list(process_item.map(["a", "b", "c", "d"]))
    print(results)
```

Omit `gpu=` for a CPU swarm. Modal scales containers automatically.

### Secrets

```python
@app.function(secrets=[modal.Secret.from_name("my-api-keys")])
def call_api():
    import os
    api_key = os.environ["API_KEY"]  # injected by secret
```

Create secrets: `modal secret create my-api-keys API_KEY=value`

### Web endpoint

```python
@app.function(gpu="A100", image=image)
@modal.web_endpoint()
def predict(prompt: str):
    return {"result": "..."}
```

Deploy: `modal deploy script.py` — returns a URL.

## Troubleshooting

- **"Modal token not found"**: Run `modal token set` or set `MODAL_TOKEN_ID` + `MODAL_TOKEN_SECRET`
- **OOM on GPU**: Use a larger GPU or reduce batch size
- **Timeout**: Increase `timeout=` parameter (default 300s)
- **Import errors in container**: Add packages to `.pip_install()` in the image definition
