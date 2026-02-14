---
name: modal
description: >
  Run compute on Modal (https://modal.com/) GPUs. Spawn containers, run scripts,
  manage volumes. Use when the user needs GPU compute, wants to run ML inference,
  train models, or execute heavy workloads in the cloud. Do NOT use for local-only
  tasks or when the user has not set up a Modal account.
allowed-tools: Bash(uv run *), Bash(modal *), Read, Write, Glob
---

Run GPU compute on Modal from your local machine. Modal provides serverless GPU containers with sub-5s cold starts — no SSH, no Kubernetes, no Docker registry.

## Prerequisites

1. **Modal account**: Sign up at https://modal.com/
2. **Modal token**: Run `modal token set` or set env vars:
   ```bash
   export MODAL_TOKEN_ID="your-token-id"
   export MODAL_TOKEN_SECRET="your-token-secret"
   ```
3. **Check auth**: `uv run --directory SKILL_DIR python scripts/modal_helper.py check-auth`

## Quick Reference

### Run a function on a GPU

```bash
modal run script.py  # runs @app.local_entrypoint()
```

### Interactive GPU shell

```bash
modal shell --gpu A100          # bare GPU shell
modal shell script.py::my_func  # shell with function's image/volumes
```

### Deploy a persistent app

```bash
modal deploy script.py  # creates versioned deployment
```

### Volume management

```bash
modal volume create my-data            # create
modal volume ls my-data                # list contents
modal volume put my-data ./local /remote  # upload
modal volume get my-data /remote ./local  # download
```

## Generating App Boilerplate

Use the helper script to generate Modal app templates:

```bash
# Basic GPU function
uv run --directory SKILL_DIR python scripts/modal_helper.py scaffold --gpu A100 --name my_app

# With pip dependencies
uv run --directory SKILL_DIR python scripts/modal_helper.py scaffold --gpu A100 --name my_app -p torch -p transformers

# With a volume
uv run --directory SKILL_DIR python scripts/modal_helper.py scaffold --gpu A100 --name my_app --volume my-data:/mnt/data

# CPU-only (no GPU)
uv run --directory SKILL_DIR python scripts/modal_helper.py scaffold --name batch_job
```

Then run it: `modal run <generated_file>.py`

## GPU Options

| GPU | VRAM | Best for |
|-----|------|----------|
| `T4` | 16 GB | Light inference, prototyping |
| `L4` | 24 GB | Inference, small fine-tuning |
| `A10G` | 24 GB | Inference, moderate training |
| `L40S` | 48 GB | Vision, inference, mid training |
| `A100` | 40/80 GB | Training, large inference |
| `H100` | 80 GB | Large-scale training |

Multi-GPU: use `A100:4` syntax for 4x GPUs.

## Modal App Patterns

### Minimal GPU function

```python
import modal

app = modal.App("my-app")
image = modal.Image.debian_slim(python_version="3.11").pip_install("torch")

@app.function(gpu="A100", image=image, timeout=3600)
def train():
    import torch
    print(f"CUDA available: {torch.cuda.is_available()}")
    print(f"Device: {torch.cuda.get_device_name(0)}")

@app.local_entrypoint()
def main():
    train.remote()
```

### With volumes for persistent storage

```python
import modal

app = modal.App("data-app")
volume = modal.Volume.from_name("my-data", create_if_missing=True)

@app.function(gpu="A100", volumes={"/mnt/data": volume}, timeout=3600)
def process():
    import os
    files = os.listdir("/mnt/data")
    print(f"Files in volume: {files}")
    # Write results — auto-committed on exit
    with open("/mnt/data/output.txt", "w") as f:
        f.write("done")

@app.local_entrypoint()
def main():
    process.remote()
```

### With secrets

```python
import modal

app = modal.App("secure-app")

@app.function(secrets=[modal.Secret.from_name("my-api-keys")])
def call_api():
    import os
    api_key = os.environ["API_KEY"]  # injected by secret
```

Create secrets in the Modal dashboard or via: `modal secret create my-api-keys API_KEY=value`

### Parallel map over inputs

```python
@app.function(gpu="T4", image=image)
def process_item(item: str) -> str:
    return f"processed: {item}"

@app.local_entrypoint()
def main():
    items = ["a", "b", "c", "d"]
    results = list(process_item.map(items))  # parallel execution
    for r in results:
        print(r)
```

## Common Workflows

### Run a local script on a GPU

1. Wrap your script in a Modal function (use `scaffold` to generate boilerplate)
2. `modal run your_modal_app.py`

### Serve an inference endpoint

```python
@app.function(gpu="A100", image=image)
@modal.web_endpoint()
def predict(prompt: str):
    # load model, run inference
    return {"result": "..."}
```

Deploy with `modal deploy script.py`, get a URL back.

### Download results from a volume

```bash
modal volume get my-data /output ./local_output
```

## Troubleshooting

- **"Modal token not found"**: Run `modal token set` or set `MODAL_TOKEN_ID` + `MODAL_TOKEN_SECRET`
- **OOM on GPU**: Use a larger GPU (`A100` instead of `T4`) or reduce batch size
- **Timeout**: Increase `timeout=` parameter (default is 300s)
- **Cold start slow**: Pre-build the image with `modal run --build` or use `modal deploy` for warm containers
- **Import errors in container**: Add missing packages to `.pip_install()` in the image definition
