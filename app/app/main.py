import random
import time

from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

app = FastAPI(title="shop-api")

REQUESTS_TOTAL = Counter(
    "shop_http_requests_total",
    "Total number of HTTP requests",
    ["method", "path", "status"],
)
REQUEST_LATENCY_SECONDS = Histogram(
    "shop_http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "path"],
    buckets=(0.01, 0.05, 0.1, 0.2, 0.35, 0.5, 1.0, 2.0, 5.0),
)


def simulate_work(base: float, jitter: float) -> None:
    sleep_for = max(0.0, random.normalvariate(base, jitter))
    time.sleep(sleep_for)


@app.get("/health")
def health() -> dict[str, str]:
    started = time.perf_counter()
    simulate_work(0.015, 0.005)
    elapsed = time.perf_counter() - started
    REQUESTS_TOTAL.labels(method="GET", path="/health", status="200").inc()
    REQUEST_LATENCY_SECONDS.labels(method="GET", path="/health").observe(elapsed)
    return {"status": "ok"}


@app.get("/")
def index() -> dict[str, str]:
    started = time.perf_counter()
    simulate_work(0.08, 0.03)

    status = "200"
    if random.random() < 0.08:
        status = "500"

    elapsed = time.perf_counter() - started
    REQUESTS_TOTAL.labels(method="GET", path="/", status=status).inc()
    REQUEST_LATENCY_SECONDS.labels(method="GET", path="/").observe(elapsed)

    if status == "500":
        raise HTTPException(status_code=500, detail="simulated upstream error")

    return {"service": "shop-api", "message": "hello from demo app"}


@app.get("/checkout")
def checkout() -> dict[str, str]:
    started = time.perf_counter()
    simulate_work(0.2, 0.08)

    status = "200"
    if random.random() < 0.15:
        status = "503"

    elapsed = time.perf_counter() - started
    REQUESTS_TOTAL.labels(method="GET", path="/checkout", status=status).inc()
    REQUEST_LATENCY_SECONDS.labels(method="GET", path="/checkout").observe(elapsed)

    if status == "503":
        raise HTTPException(status_code=503, detail="simulated payment provider timeout")

    return {"result": "order accepted"}


@app.get("/metrics")
def metrics() -> PlainTextResponse:
    payload = generate_latest()
    return PlainTextResponse(payload.decode("utf-8"), media_type=CONTENT_TYPE_LATEST)
