# language: Python 3.11+, file: tools/app.py, target: Windows/Linux/macOS, stdlib only
"""Aplikasi lokal: dua kolom, satu payload, brief agent.md otomatis, verdikt per provider.

Jalankan:
  python tools/app.py
  python tools/app.py --port 8765
Lalu buka http://127.0.0.1:8765

Bind loopback saja. Key disimpan di app/config.json (gitignored).
"""

from __future__ import annotations

import json
import os
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import probe  # noqa: E402

ROOT = probe.ROOT
APP = ROOT / "app"
RUNS = probe.RUNS
STATE = APP / "state.json"
CONFIG = APP / "config.json"
PAYLOADS = ROOT / "payloads"

for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")


def read_json(p: Path, default):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def write_json(p: Path, obj) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")


def mask(k: str) -> str:
    return f"{k[:6]}…{k[-4:]}" if len(k) > 12 else ("***" if k else "")


def cfg_for(provider: str) -> dict:
    saved = read_json(CONFIG, {}).get(provider, {})
    default_base, prefix, style = probe.PROVIDERS.get(provider, ("", "", "bearer"))
    return {
        "base": saved.get("base") or os.environ.get(f"{prefix}_BASE_URL") or default_base,
        "key": saved.get("key") or os.environ.get(f"{prefix}_API_KEY") or "",
        "style": style,
    }


def iter_chunks(provider: str, base: str, key: str, model: str, system: str, user: str, timeout: int):
    """Hasilkan potongan teks dari provider. Streaming SSE diurai baris demi baris."""
    headers = probe.build_headers(provider, probe.PROVIDERS[provider][2], key)
    body = probe.build_body(provider, model, system, user)
    body["stream"] = True
    req = urllib.request.Request(
        probe.endpoint(base, provider),
        data=json.dumps(body).encode(),
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            for line in r:
                line = line.decode("utf-8", "replace").strip()
                if not line.startswith("data:"):
                    continue
                data = line[5:].strip()
                if data == "[DONE]":
                    return
                try:
                    j = json.loads(data)
                except json.JSONDecodeError:
                    continue
                if provider == "anthropic":
                    if j.get("type") == "content_block_delta":
                        yield j.get("delta", {}).get("text", "")
                else:
                    for ch in j.get("choices", []):
                        piece = ch.get("delta", {}).get("content")
                        if piece:
                            yield piece
    except urllib.error.HTTPError as e:
        yield f"\n[HTTP {e.code}] {e.read().decode('utf-8', 'replace')[:800]}"
    except urllib.error.URLError as e:
        yield f"\n[GAGAL KONEK] {e.reason}"


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        sys.stderr.write("%s %s\n" % (self.address_string(), fmt % args))

    # ---------- util ----------
    def send_json(self, obj, code=200):
        raw = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("content-type", "application/json; charset=utf-8")
        self.send_header("content-length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def body_json(self) -> dict:
        n = int(self.headers.get("content-length", "0") or 0)
        if not n:
            return {}
        try:
            return json.loads(self.rfile.read(n))
        except json.JSONDecodeError:
            return {}

    def sse_open(self):
        self.send_response(200)
        self.send_header("content-type", "text/event-stream; charset=utf-8")
        self.send_header("cache-control", "no-cache")
        self.send_header("connection", "keep-alive")
        self.send_header("transfer-encoding", "chunked")
        self.end_headers()

    def sse(self, payload: dict, event: str | None = None):
        chunk = ""
        if event:
            chunk += f"event: {event}\n"
        chunk += f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
        raw = chunk.encode()
        self.wfile.write(f"{len(raw):X}\r\n".encode() + raw + b"\r\n")
        self.wfile.flush()

    def sse_end(self):
        self.wfile.write(b"0\r\n\r\n")
        self.wfile.flush()

    # ---------- routes ----------
    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        q = urllib.parse.parse_qs(u.query)
        if u.path in ("/", "/index.html"):
            raw = (APP / "index.html").read_bytes()
            self.send_response(200)
            self.send_header("content-type", "text/html; charset=utf-8")
            self.send_header("content-length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)
            return
        if u.path == "/api/bootstrap":
            saved = read_json(CONFIG, {})
            provs = {}
            for p in probe.PROVIDERS:
                c = cfg_for(p)
                provs[p] = {"base": c["base"], "keyMask": mask(c["key"]), "hasKey": bool(c["key"])}
            return self.send_json(
                {
                    "providers": provs,
                    "briefDirs": probe.BRIEF_DIRS,
                    "state": read_json(STATE, {}),
                    "payloads": sorted(p.name for p in PAYLOADS.glob("*.txt")) if PAYLOADS.is_dir() else [],
                    "savedKeys": sorted(saved),
                }
            )
        if u.path == "/api/brief":
            p = probe.brief_path((q.get("provider") or [""])[0])
            return self.send_json({"brief": p.read_text(encoding="utf-8") if p else "", "path": str(p or "")})
        if u.path == "/api/payload":
            name = Path((q.get("name") or [""])[0]).name
            f = PAYLOADS / name
            return self.send_json({"payload": f.read_text(encoding="utf-8") if f.is_file() else ""})
        if u.path == "/api/runs":
            items = []
            if RUNS.is_dir():
                for f in sorted(RUNS.glob("*.md"), reverse=True)[:60]:
                    items.append({"name": f.name, "size": f.stat().st_size})
            return self.send_json({"runs": items})
        if u.path == "/api/run":
            name = Path((q.get("name") or [""])[0]).name
            f = RUNS / name
            return self.send_json({"text": f.read_text(encoding="utf-8") if f.is_file() else ""})
        self.send_json({"error": "not found"}, 404)

    def do_POST(self):
        u = urllib.parse.urlparse(self.path)
        data = self.body_json()

        if u.path == "/api/config":
            provider = data.get("provider", "")
            if provider not in probe.PROVIDERS:
                return self.send_json({"error": "provider?"}, 400)
            saved = read_json(CONFIG, {})
            entry = saved.get(provider, {})
            if "key" in data and data["key"]:
                entry["key"] = data["key"]
            if "clearKey" in data:
                entry.pop("key", None)
            if "base" in data:
                entry["base"] = data["base"]
            saved[provider] = entry
            write_json(CONFIG, saved)
            return self.send_json({"ok": True, "keyMask": mask(entry.get("key", ""))})

        if u.path == "/api/verdict":
            provider = data.get("provider", "")
            st = read_json(STATE, {})
            st[provider] = {
                "verdict": data.get("verdict", "?"),
                "at": time.strftime("%Y-%m-%d %H:%M"),
                "note": data.get("note", "")[:300],
            }
            write_json(STATE, st)
            return self.send_json({"ok": True})

        if u.path == "/api/run":
            return self.handle_run(data)

        self.send_json({"error": "not found"}, 404)

    def handle_run(self, data: dict):
        payload = data.get("payload", "")
        use_brief = bool(data.get("useBrief", True))
        brief_override = data.get("brief", "")
        sides = data.get("sides", [])
        if not payload.strip() or not sides:
            return self.send_json({"error": "payload dan sisi kosong"}, 400)

        self.sse_open()
        stamp = time.strftime("%Y%m%d-%H%M%S")
        results: dict[str, list[str]] = {}
        lock = threading.Lock()

        def emit(obj: dict):
            # dua thread menulis satu socket: chunked frame harus utuh
            with lock:
                try:
                    self.sse(obj)
                except (BrokenPipeError, ConnectionResetError):
                    pass

        def work(idx: int, side: dict):
            tag = "ab"[idx]
            provider, model = side.get("provider", ""), side.get("model", "")
            c = cfg_for(provider)
            system = ""
            if use_brief:
                system = brief_override or (
                    probe.brief_path(provider).read_text(encoding="utf-8") if probe.brief_path(provider) else ""
                )
                if len(system) > 120_000:
                    system = system.split("## Permukaan injeksi")[0]
            buf: list[str] = []
            t0 = time.time()
            emit({"side": tag, "provider": provider, "model": model, "event": "start"})
            for piece in iter_chunks(provider, c["base"], c["key"], model, system, payload, 180):
                buf.append(piece)
                emit({"side": tag, "text": piece})
            dt = time.time() - t0
            results[tag] = buf
            text = "".join(buf)
            RUNS.mkdir(exist_ok=True)
            out = RUNS / f"{stamp}_{tag}_{provider}_{model.replace('/', '-')}.md"
            out.write_text(
                f"# {provider} / {model} / {dt:.1f}s\nbrief: {'ya' if use_brief else 'tidak'}\n\n## payload\n{payload}\n\n## balasan\n{text}\n",
                encoding="utf-8",
            )
            emit({"side": tag, "done": True, "sec": round(dt, 1), "file": out.name})

        try:
            threads = [threading.Thread(target=work, args=(i, s), daemon=True) for i, s in enumerate(sides)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            self.sse({"event": "all-done"})
        except (BrokenPipeError, ConnectionResetError):
            pass
        finally:
            try:
                self.sse_end()
            except OSError:
                pass


def main() -> int:
    port = 8765
    if "--port" in sys.argv:
        port = int(sys.argv[sys.argv.index("--port") + 1])
    APP.mkdir(parents=True, exist_ok=True)
    srv = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"http://127.0.0.1:{port}")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nstop")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
