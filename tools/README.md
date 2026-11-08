# tools/

`probe.py` — kirim payload ke provider, `agent.md` provider otomatis jadi system prompt, hasil disimpan di `runs/`.

Key dan base URL bisa ditanam langsung di perintah, lewat env, atau lewat `.env` (salin `.env.example`).

## Contoh

```bat
:: key + base tertanam di perintah
python tools\probe.py openai --model gpt-5 --key sk-... --base-url https://api.openai.com/v1 --file payload.txt

:: base URL sendiri (gateway / proxy / vLLM)
python tools\probe.py openai --model gpt-5 --key sk-local --base-url http://127.0.0.1:8000/v1 --payload "halo"

:: model lokal tanpa key (ollama 11434, llama.cpp 8080)
python tools\probe.py local --model qwen2.5 --base-url http://127.0.0.1:11434/v1 --payload "halo"

:: anthropic (x-api-key, /messages)
python tools\probe.py anthropic --model claude-opus-4-5 --file payload.txt

:: cek request dulu, tidak dikirim
python tools\probe.py openai --model gpt-5 --payload "halo" --dry
```

## Flag

| flag | arti |
|---|---|
| `--key` | API key, menang atas env `<PROVIDER>_API_KEY` |
| `--base-url` | override base, menang atas `<PROVIDER>_BASE_URL` |
| `--payload` / `--file` | isi pesan user |
| `--brief` / `--no-brief` | ganti atau matikan system prompt |
| `--dry` | cetak request, tidak kirim |
| `--timeout` | detik, default 180 |

Brief dipotong di penanda `## Permukaan injeksi` bila lebih dari 120 KB. Untuk kirim utuh: `--ignore-brief-marker`.

Provider bawaan: openai, openrouter, xai, mistral, moonshot, deepseek, zai, minimax, local, anthropic. Semua OpenAI-compatible kecuali anthropic.

Uji: `python tools/test_probe.py`
