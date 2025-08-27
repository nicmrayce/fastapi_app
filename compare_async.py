import asyncio, time, itertools, sys, math, httpx

URL = "http://127.0.0.1:8000"
N = 5
CONCURRENCY = 5
TIMEOUT = 60.0

async def spinner(msg="Loading"):
    for c in itertools.cycle("|/-\\"):
        sys.stdout.write(f"\r{msg} {c}")
        sys.stdout.flush()
        try:
            await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            break
    sys.stdout.write("\r" + " " * (len(msg) + 2) + "\r")

async def run_batch(endpoint: str) -> float:
    limits = httpx.Limits(max_connections=CONCURRENCY, max_keepalive_connections=CONCURRENCY)
    timeout = httpx.Timeout(TIMEOUT, connect=TIMEOUT, read=TIMEOUT, write=TIMEOUT)
    sem = asyncio.Semaphore(CONCURRENCY)

    async with httpx.AsyncClient(limits=limits, timeout=timeout) as client:
        ok = 0
        async def one_call(i: int):
            nonlocal ok
            async with sem:
                try:
                    r = await client.get(f"{URL}/{endpoint}")
                    if r.status_code == 200:
                        ok += 1
                except Exception:
                    pass

        start = time.time()
        spin = asyncio.create_task(spinner(f"Running {endpoint}"))
        try:
            await asyncio.gather(*(one_call(i) for i in range(N)))
        finally:
            spin.cancel()  # <-- stop spinner
        elapsed = time.time() - start
        print(f"{endpoint}: {ok}/{N} succeeded")
        return elapsed

async def main():
    print(f"Sending {N} requests with concurrency={CONCURRENCY}\n")
    t_sync = await run_batch("sync-slow")
    print(f"sync-slow took  {t_sync:.2f}s\n")
    t_async = await run_batch("async-slow")
    print(f"async-slow took {t_async:.2f}s\n")

    print("HTTP I/O comparison:")
    t_sync_h = await run_batch("sync-http")
    print(f"sync-http took  {t_sync_h:.2f}s")
    t_async_h = await run_batch("async-http")
    print(f"async-http took {t_async_h:.2f}s")

if __name__ == "__main__":
    asyncio.run(main())
