# tools/

Dua pintu masuk, satu mesin (`probe.py`).

## Aplikasi lokal — `app.py`

```bat
python tools\app.py
```
Buka http://127.0.0.1:8765

Dua kolom bicara. Payload sama dikirim ke dua model sekaligus, mengalir berdampingan. Brief provider A terisi otomatis dan bisa diedit. Sesudah run, tombol verdikt `lulus` / `gagal` / `mati` per provider — tersimpan, muncul sebagai lencana.

Bind loopback saja. Key disimpan di `app/config.json` (gitignored).

## CLI — `probe.py`

```bat
python tools\probe.py openai --model gpt-5 --key sk-... --base-url https://api.openai.com/v1 --file payload.txt
python tools\probe.py local --model qwen2.5 --base-url http://127.0.0.1:11434/v1 --payload "halo"
python tools\probe.py anthropic --model claude-opus-4-5 --file payload.txt
python tools\probe.py openai --model gpt-5 --payload "halo" --dry
```

Flag: `--key`, `--base-url`, `--payload`/`--file`, `--brief`/`--no-brief`, `--dry`, `--timeout`.
Urutan menang: flag > env `<PROVIDER>_API_KEY` > `.env`.

Provider: openai, openrouter, xai, mistral, moonshot, deepseek, zai, minimax, local, anthropic.
Semua OpenAI-compatible kecuali anthropic (`x-api-key`, `/messages`).

Brief dipotong di `## Permukaan injeksi` bila > 120 KB (CLI: `--ignore-brief-marker`).

## Uji

```bat
python tools\test_probe.py
python tools\test_app.py
```
`test_app.py` memakai provider palsu — tidak butuh key.
