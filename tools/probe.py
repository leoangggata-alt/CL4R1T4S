# language: Python 3.11+, file: tools/probe.py, target: Windows/Linux/macOS, stdlib only
# *no SDK, no deps. urllib only. jsonapi shapes: openai-compatible + anthropic.*
"""Kirim payload ke provider, brief agent.md otomatis jadi system prompt.

Pemakaian:
  set OPENAI_API_KEY=sk-...            # key per provider, nama env: <PROVIDER>_API_KEY
  set OPENAI_BASE_URL=https://.../v1   # opsional, override base
  python tools/probe.py openai --model gpt-5 --file payloads/openai_01.txt

  python tools/probe.py anthropic --model claude-opus-4-5 --payload "probe identitas"
  python tools/probe.py local --model qwen --file p.txt          # llama.cpp/ollama, key opsional
  python tools/probe.py openai --model gpt-5 --file p.txt --dry # cetak request, jangan kirim
  python tools/probe.py openai --model gpt-5 --file p.txt --no-brief

Key & base juga bisa dari flag: --key, --base-url. File .env di root repo dibaca otomatis.
Hasil disimpan di runs/, satu file per panggilan.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUNS = ROOT / "runs"

for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

# provider -> (default base_url, env prefix, gaya auth)
PROVIDERS = {
    "openai": ("https://api.openai.com/v1", "OPENAI", "bearer"),
    "openrouter": ("https://openrouter.ai/api/v1", "OPENROUTER", "bearer"),
    "xai": ("https://api.x.ai/v1", "XAI", "bearer"),
    "mistral": ("https://api.mistral.ai/v1", "MISTRAL", "bearer"),
    "moonshot": ("https://api.moonshot.ai/v1", "MOONSHOT", "bearer"),
    "deepseek": ("https://api.deepseek.com/v1", "DEEPSEEK", "bearer"),
    "zai": ("https://api.z.ai/api/paas/v4", "ZAI", "bearer"),
    "minimax": ("https://api.minimax.io/v1", "MINIMAX", "bearer"),
    "local": ("http://127.0.0.1:8080/v1", "LOCAL", "bearer"),
    "anthropic": ("https://api.anthropic.com/v1", "ANTHROPIC", "x-api-key"),
}

BRIEF_DIRS = {
    "openai": "OPENAI",
    "openrouter": "OPENAI",
    "anthropic": "ANTHROPIC",
    "xai": "XAI",
    "mistral": "MISTRAL",
    "moonshot": "MOONSHOT",
    "deepseek": "MISTRAL",
    "minimax": "MINIMAX",
    "zai": "ZAI/ZCode",
    "local": "",
}


def load_dotenv() -> None:
    """Baca .env sederhana: K=V per baris, abaikan komentar. Tidak menimpa env asli."""
    f = ROOT / ".env"
    if not f.is_file():
        return
    for line in f.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip().strip("'\""))


def brief_path(provider: str) -> Path | None:
    d = BRIEF_DIRS.get(provider, provider)
    p = ROOT / d / "agent.md"
    return p if p.is_file() else None


def build_body(provider: str, model: str, system: str, user: str) -> dict:
    if provider == "anthropic":
        body = {
            "model": model,
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": user}],
        }
        if system:
            body["system"] = system
        return body
    msgs = []
    if system:
        msgs.append({"role": "system", "content": system})
    msgs.append({"role": "user", "content": user})
    return {"model": model, "messages": msgs, "stream": False}


def build_headers(provider: str, style: str, key: str) -> dict:
    h = {"content-type": "application/json", "user-agent": "probe/1.0"}
    if style == "x-api-key":
        h["x-api-key"] = key
        h["anthropic-version"] = "2023-06-01"
    elif key:
        h["authorization"] = f"Bearer {key}"
    return h


def endpoint(base: str, provider: str) -> str:
    return base.rstrip("/") + ("/messages" if provider == "anthropic" else "/chat/completions")


def send(url: str, headers: dict, body: dict, timeout: int) -> tuple[int, str]:
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except urllib.error.URLError as e:
        return 0, f"URLError: {e.reason}"


def extract(provider: str, raw: str) -> str:
    """Ambil teks balasan. Bentuk asing -> kembalikan mentah."""
    try:
        j = json.loads(raw)
    except json.JSONDecodeError:
        return raw
    if provider == "anthropic":
        parts = [b.get("text", "") for b in j.get("content", []) if isinstance(b, dict)]
        return "".join(parts) or raw
    try:
        return j["choices"][0]["message"]["content"] or raw
    except (KeyError, IndexError, TypeError):
        return raw


def main() -> int:
    ap = argparse.ArgumentParser(description="kirim payload ke provider, brief agent.md sebagai system")
    ap.add_argument("provider", choices=sorted(PROVIDERS))
    ap.add_argument("--model", required=True)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--payload", help="teks payload langsung")
    g.add_argument("--file", help="file payload")
    ap.add_argument("--brief", help="ganti file brief (default: <PROVIDER>/agent.md)")
    ap.add_argument("--no-brief", action="store_true", help="tanpa system prompt")
    ap.add_argument("--key", help="API key (default: env <PROVIDER>_API_KEY)")
    ap.add_argument("--base-url", help="override base URL")
    ap.add_argument("--timeout", type=int, default=180)
    ap.add_argument("--dry", action="store_true", help="cetak request tanpa mengirim")
    ap.add_argument("--ignore-brief-marker", action="store_true", help="kirim brief utuh walau > 120 KB")
    a = ap.parse_args()

    load_dotenv()
    default_base, prefix, style = PROVIDERS[a.provider]
    base = a.base_url or os.environ.get(f"{prefix}_BASE_URL") or default_base
    key = a.key or os.environ.get(f"{prefix}_API_KEY") or ""

    if a.file:
        user = Path(a.file).read_text(encoding="utf-8")
    else:
        user = a.payload

    system = ""
    bp = Path(a.brief) if a.brief else brief_path(a.provider)
    if bp and not a.no_brief:
        system = bp.read_text(encoding="utf-8")
        if len(system) > 120_000 and not a.ignore_brief_marker:
            system = system.split("## Permukaan injeksi")[0] + "\n(brief dipotong: pakai --ignore-brief-marker untuk utuh)"

    if not key and a.provider != "local":
        print(f"!! {prefix}_API_KEY kosong. set env atau pakai --key.", file=sys.stderr)

    url = endpoint(base, a.provider)
    headers = build_headers(a.provider, style, key)
    body = build_body(a.provider, a.model, system, user)

    masked = {k: ("***" if k.lower() in ("authorization", "x-api-key") else v) for k, v in headers.items()}
    if a.dry:
        print(f"POST {url}")
        print(json.dumps(masked, indent=2))
        print(json.dumps(body, indent=2, ensure_ascii=False)[:2000])
        return 0

    t0 = time.time()
    status, raw = send(url, headers, body, a.timeout)
    dt = time.time() - t0
    text = extract(a.provider, raw)

    RUNS.mkdir(exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    out = RUNS / f"{stamp}_{a.provider}_{a.model.replace('/', '-')}.md"
    out.write_text(
        f"# {a.provider} / {a.model} / {status} / {dt:.1f}s\n"
        f"brief: {bp if system else 'none'}\n\n## payload\n{user}\n\n## balasan\n{text}\n",
        encoding="utf-8",
    )

    print(text)
    print(f"\n-- {status} · {dt:.1f}s · {out.relative_to(ROOT)}", file=sys.stderr)
    return 0 if status == 200 else 1


if __name__ == "__main__":
    raise SystemExit(main())
