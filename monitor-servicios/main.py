import os
import json
import time
import socket
import threading
import requests
from datetime import datetime, timezone, timedelta
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

CHECK_INTERVAL = 10
RETENTION_MINUTES = 10
DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "monitor.json")

SERVICES = {
    "backend": {"url": "http://backend:3000/", "label": "Backend API"},
    "frontend": {"url": "http://frontend:80/", "label": "Frontend Web"},
    "mongodb": {"url": None, "label": "MongoDB"},
}

_data = {name: [] for name in SERVICES}
_lock = threading.Lock()


def _load_data():
    global _data
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                _data = json.load(f)
        except Exception:
            _data = {name: [] for name in SERVICES}
    for name in SERVICES:
        _data.setdefault(name, [])


def _prune():
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=RETENTION_MINUTES)
    for name in list(_data.keys()):
        _data[name] = [
            c for c in _data[name]
            if datetime.fromisoformat(c["fecha"]).replace(tzinfo=timezone.utc) > cutoff
        ]


def _save_data():
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with _lock:
        _prune()
        with open(DATA_FILE, "w") as f:
            json.dump(_data, f, indent=2, default=str)


def _add_check(servicio, status, response_time_ms, error=None):
    check = {
        "servicio": servicio,
        "status": status,
        "response_time_ms": response_time_ms,
        "error": error,
        "fecha": datetime.now(timezone.utc).isoformat(),
    }
    with _lock:
        _data.setdefault(servicio, [])
        _data[servicio].append(check)
        _prune()


def _check_http(name, url):
    start = time.time()
    try:
        r = requests.get(url, timeout=10)
        elapsed_ms = int((time.time() - start) * 1000)
        if r.status_code < 500:
            _add_check(name, "online", elapsed_ms)
        else:
            _add_check(name, "offline", elapsed_ms, f"HTTP {r.status_code}")
    except Exception as e:
        elapsed_ms = int((time.time() - start) * 1000)
        _add_check(name, "offline", elapsed_ms, str(e))


def _check_mongo(name):
    start = time.time()
    try:
        s = socket.create_connection(("mongodb", 27017), timeout=5)
        s.close()
        elapsed_ms = int((time.time() - start) * 1000)
        _add_check(name, "online", elapsed_ms)
    except Exception as e:
        elapsed_ms = int((time.time() - start) * 1000)
        _add_check(name, "offline", elapsed_ms, str(e))


def _run_checks():
    while True:
        for name, cfg in SERVICES.items():
            if cfg["url"]:
                _check_http(name, cfg["url"])
            else:
                _check_mongo(name)
        _save_data()
        time.sleep(CHECK_INTERVAL)


_load_data()
_thread = threading.Thread(target=_run_checks, daemon=True)
_thread.start()

app = FastAPI(title="Monitor de Servicios")

static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
async def dashboard():
    html_path = os.path.join(static_dir, "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r") as f:
            return HTMLResponse(f.read())
    return HTMLResponse("<h1>Monitor</h1><p>Dashboard no encontrado</p>")


@app.get("/api/monitor/status")
async def get_status():
    result = {}
    for name in SERVICES:
        checks = _data.get(name, [])
        result[name] = checks[-1] if checks else None
    return result


@app.get("/api/monitor/history")
async def get_history(service: str = Query(None), limit: int = Query(100)):
    if service:
        logs = list(reversed(_data.get(service, [])))
    else:
        logs = []
        for name in SERVICES:
            logs.extend(_data.get(name, []))
        logs.sort(key=lambda x: x["fecha"], reverse=True)
    return logs[:limit]


@app.get("/api/monitor/stats")
async def get_stats():
    stats = {}
    for name in SERVICES:
        checks = _data.get(name, [])
        total = len(checks)
        online = sum(1 for c in checks if c["status"] == "online")
        uptime_pct = round((online / total * 100), 1) if total > 0 else 0
        last = checks[-1] if checks else None
        avg_response = (
            round(sum(c["response_time_ms"] for c in checks) / total)
            if total > 0 else 0
        )
        stats[name] = {
            "label": SERVICES[name]["label"],
            "uptime_pct": uptime_pct,
            "total_checks": total,
            "online_checks": online,
            "offline_checks": total - online,
            "avg_response_ms": avg_response,
            "last_status": last["status"] if last else "unknown",
            "last_check": last["fecha"] if last else None,
        }
    return stats
