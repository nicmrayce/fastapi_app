# FastAPI Async vs Sync — Performance Demo
By Nic M Rayce

This project demonstrates **real-world differences between synchronous and asynchronous I/O** in FastAPI using:

* `time.sleep()` vs `asyncio.sleep()`
* `requests` (blocking) vs `httpx` (async)
* HuggingFace + RunPod mock integrations
* Background tasks + S3 client
* CI/CD with GitHub Actions
* Unit tests with full mocking

The project includes a benchmark tool (`compare_async.py`) that clearly shows how concurrency behaves under sync vs async.

---

## 🚀 Getting Started

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run the app

```bash
uvicorn apiapp.main:app --reload
```

API Docs → [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 📁 Project Structure

```
fastApi/
├── apiapp/
│   ├── main.py
│   ├── models.py
│   ├── deps.py
│   ├── settings.py
│   ├── services/
│   │   ├── hf.py
│   │   ├── runpod.py
│   │   └── s3.py
├── tests/
│   └── test_api.py
├── compare_async.py
├── requirements.txt
└── README.md
```

---

## 🧪 Run Tests

```bash
pytest -q
```

GitHub Actions runs these same tests automatically on every commit.

---

## ⚡ Benchmark Script (Async vs Sync)

Run:

```bash
python compare_async.py
```

Example output:

```
sync-slow took  24.18s
async-slow took 2.03s

sync-http took  40.21s
async-http took 6.33s
```

---

## 🧠 Threadpool Capping (important)

To ensure consistent benchmark behaviour:

```python
from anyio.to_thread import current_default_thread_limiter

@app.on_event("startup")
async def cap_threadpools():
    loop = asyncio.get_running_loop()
    loop.set_default_executor(ThreadPoolExecutor(max_workers=1))
    current_default_thread_limiter().total_tokens = 1
```

This forces synchronous I/O to serialize while async I/O overlaps correctly.

---

## 🧹 .gitignore

```
# Python
__pycache__/
*.pyc

# Environment
venv/
.env

# IDE
.vscode/
.idea/

# Tests
.pytest_cache/
.coverage
```

---

## 🛠️ CI/CD (GitHub Actions)

`.github/workflows/tests.yml`:

```yaml
name: CI Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.9"
      - run: pip install -r requirements.txt
      - run: pytest -q
```

---
