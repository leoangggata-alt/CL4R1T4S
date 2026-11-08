# language: Python 3.11+, file: tools/test_app.py, jalankan: python tools/test_app.py
"""Uji app.py end-to-end dengan provider palsu (tanpa API key)."""
import json
import subprocess
import sys
import threading
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FAKE_PORT = 8798
APP_PORT = 8799


class Fake(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *a):
        pass

    def do_POST(self):
        n = int(self.headers.get("content-length", "0") or 0)
        body = json.loads(self.rfile.read(n) or b"{}")
        assert body["messages"][-1]["role"] == "user", body
        self.send_response(200)
        self.send_header("content-type", "text/event-stream")
        self.send_header("transfer-encoding", "chunked")
        self.end_headers()
        for piece in ["sa", "tu", " dua"]:
            frame = f'data: {json.dumps({"choices": [{"delta": {"content": piece}}]})}\n\n'.encode()
            self.wfile.write(f"{len(frame):X}\r\n".encode() + frame + b"\r\n")
            self.wfile.flush()
        self.wfile.write(b"data: [DONE]\n\n")
        self.wfile.write(b"0\r\n\r\n")
        self.wfile.flush()


def get(path, base=f"http://127.0.0.1:{APP_PORT}"):
    with urllib.request.urlopen(base + path, timeout=20) as r:
        return json.loads(r.read())


def post(path, obj):
    req = urllib.request.Request(
        f"http://127.0.0.1:{APP_PORT}{path}",
        data=json.dumps(obj).encode(),
        headers={"content-type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode()


def main() -> int:
    fake = ThreadingHTTPServer(("127.0.0.1", FAKE_PORT), Fake)
    threading.Thread(target=fake.serve_forever, daemon=True).start()

    proc = subprocess.Popen(
        [sys.executable, str(ROOT / "tools" / "app.py"), "--port", str(APP_PORT)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        for _ in range(60):
            try:
                boot = get("/api/bootstrap")
                break
            except OSError:
                time.sleep(0.1)
        else:
            raise RuntimeError("server tidak siap")

        assert "providers" in boot and "openai" in boot["providers"], boot
        assert isinstance(get("/api/brief?provider=openai")["brief"], str)
        assert "Model apa kamu" in get("/api/payload?name=01_probe.txt")["payload"]

        with urllib.request.urlopen(f"http://127.0.0.1:{APP_PORT}/", timeout=10) as r:
            assert b"reference" not in r.read()[:200].lower()

        post("/api/config", {"provider": "openai", "key": "k", "base": f"http://127.0.0.1:{FAKE_PORT}"})
        post("/api/verdict", {"provider": "openai", "verdict": "lulus"})
        assert get("/api/bootstrap")["state"]["openai"]["verdict"] == "lulus"

        stream = post(
            "/api/run",
            {
                "payload": "halo",
                "useBrief": True,
                "sides": [{"provider": "openai", "model": "fake-a"}, {"provider": "openai", "model": "fake-b"}],
            },
        )
        seen = {"a": "", "b": ""}
        for frame in stream.split("\n\n"):
            m = frame.strip()
            if not m.startswith("data: "):
                continue
            j = json.loads(m[6:])
            if "text" in j:
                seen[j["side"]] += j["text"]
        assert seen == {"a": "satu dua", "b": "satu dua"}, seen
        assert stream.count('"done": true') == 2, stream[-400:]
        assert "HTTP" not in stream, stream[:400]
    finally:
        proc.terminate()
        fake.shutdown()

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
