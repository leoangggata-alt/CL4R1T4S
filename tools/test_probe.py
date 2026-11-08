# language: Python 3.11+, file: tools/test_probe.py, jalankan: python tools/test_probe.py
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import probe  # noqa: E402


def test_anthropic_shape():
    b = probe.build_body("anthropic", "claude-x", "SYS", "USER")
    assert b["system"] == "SYS"
    assert b["messages"] == [{"role": "user", "content": "USER"}]
    assert "max_tokens" in b
    h = probe.build_headers("anthropic", "x-api-key", "k")
    assert h["x-api-key"] == "k" and "anthropic-version" in h and "authorization" not in h


def test_openai_shape():
    b = probe.build_body("openai", "gpt-x", "SYS", "USER")
    assert [m["role"] for m in b["messages"]] == ["system", "user"]
    b2 = probe.build_body("openai", "gpt-x", "", "USER")
    assert [m["role"] for m in b2["messages"]] == ["user"]
    h = probe.build_headers("openai", "bearer", "k")
    assert h["authorization"] == "Bearer k"


def test_endpoint():
    assert probe.endpoint("https://a/v1/", "anthropic") == "https://a/v1/messages"
    assert probe.endpoint("https://a/v1", "openai") == "https://a/v1/chat/completions"


def test_extract():
    body = json.dumps({"choices": [{"message": {"content": "halo"}}]})
    assert probe.extract("openai", body) == "halo"
    anth = json.dumps({"content": [{"type": "text", "text": "yo"}]})
    assert probe.extract("anthropic", anth) == "yo"
    assert probe.extract("openai", "bukan json") == "bukan json"


def test_brief_lookup():
    assert probe.brief_path("zai") and probe.brief_path("zai").name == "agent.md"
    assert probe.brief_path("openai").parent.name == "OPENAI"
    assert probe.brief_path("anthropic").parent.name == "ANTHROPIC"
    assert probe.brief_path("local") is None


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
    print("ok")
