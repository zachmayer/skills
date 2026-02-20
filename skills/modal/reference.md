# Modal Advanced Reference

## Contents
- Modal 1.0 API changes
- Secrets
- Sandboxes
- Dicts and Queues
- Cloud bucket mounts
- GPU memory snapshots

## Modal 1.0 API Changes

Modal 1.0 (May 2025) renamed several APIs. Use the new names:

| Old (deprecated) | New (Modal 1.0+) |
|---|---|
| `modal.Stub` | `modal.App` |
| `.lookup()` | `.from_name()` |
| `allow_concurrent_inputs=N` | `@modal.concurrent(max_inputs=N)` decorator |
| `max_inputs=1` | `single_use_containers=True` |
| `keep_warm=N` | `min_containers=N` |
| `container_idle_timeout=N` | `scaledown_window=N` |
| `mount=modal.Mount(...)` | `Image.add_local_file/dir/python_source` |
| Custom `__init__` on `@app.cls` | `modal.parameter()` + `@modal.enter()` |
| `@modal.build` | Deprecated; use `Image.run_function()` |

Always use latest Modal (`uv add modal`). [Migration guide](https://modal.com/docs/guide/modal-1-0-migration)

## Secrets

```python
@app.function(secrets=[modal.Secret.from_name("my-api-keys")])
def call_api():
    import os
    api_key = os.environ["API_KEY"]  # injected by secret
```

Create: `uv run modal secret create my-api-keys API_KEY=value`
[Secrets guide](https://modal.com/docs/guide/secrets)

## Sandboxes (Running Untrusted Code)

Isolated containers built on gVisor. Not authorized to access workspace resources.

```python
sandbox = modal.Sandbox.create(
    image=my_image,
    block_network=True,
    timeout=30,
)
process = sandbox.exec("python", "script.py")
print(process.stdout.read())
sandbox.terminate()
```

Tips: use `single_use_containers=True`, `block_network=True` or `cidr_allowlist` for isolation.
[Sandboxes guide](https://modal.com/docs/guide/sandboxes)

## Dicts and Queues

Distributed data structures for inter-container communication.

```python
# Key-value store
d = modal.Dict.from_name("my-dict", create_if_missing=True)
d["key"] = "value"

# Job queue
q = modal.Queue.from_name("my-queue", create_if_missing=True)
q.put("item")
item = q.get(timeout=5)
items = q.get_many(100, timeout=5)
```

Both support ephemeral mode: `with modal.Dict.ephemeral() as d: ...`

## Cloud Bucket Mounts (S3/GCS)

```python
bucket_secret = modal.Secret.from_name("s3-creds",
    required_keys=["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"])

@app.function(volumes={
    "/mnt/bucket": modal.CloudBucketMount("my-bucket", secret=bucket_secret)
})
def process():
    files = os.listdir("/mnt/bucket")
```

## GPU Memory Snapshots (Experimental)

Snapshot GPU state after model load for faster cold starts:

```python
@app.cls(gpu="A10G", enable_memory_snapshot=True)
class Model:
    @modal.enter(snap=True)
    def load(self):
        self.model = load_model()

    @modal.method()
    def predict(self, x):
        return self.model(x)
```

Must deploy first (`uv run modal deploy`). [Cold start guide](https://modal.com/docs/guide/cold-start)
