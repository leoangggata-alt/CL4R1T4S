# AGENT INDEX — CL4R1T4S

Satu `agent.md` per provider. Tiap file memuat: slot map instruksi, guardrail verbatim, permukaan injeksi, payload base, probe verifikasi, jebakan.

## Aturan pakai
1. Baca `agent.md` provider dulu — **jangan** dump file prompt penuh ke konteks.
2. Isi prompt asli hanya untuk mengonfirmasi kutipan yang dipakai.
3. Setiap klaim di file adalah hipotesis terhadap snapshot. Probe dulu, baru percaya.
4. Snapshot basi = prompt mati. Cek tanggal di header; lebih dari 2–3 bulan, verifikasi sebelum pakai.

## Peta

| Provider | Kelas | Tuas terkuat | Snapshot |
|---|---|---|---|
| [ANTHROPIC](ANTHROPIC/agent.md) | chat + CLI | mode gaya, aturan no-apology | Jun 2024–2026 |
| [OPENAI](OPENAI/agent.md) | chat + codex + atlas | policy hanya di guardian_tool | Apr 2025–2026 |
| [GOOGLE](GOOGLE/agent.md) | chat + canvas | blok ` ```thought `/` ```tool_code ` | Apr 2025 |
| [XAI](XAI/agent.md) | chat + X search | `instructions` di `browse_page` | Mar–Nov 2025 |
| [META](META/agent.md) | chat mirroring | `do not refuse to respond EVER` | Jul 2025 / Apr 2026 |
| [MISTRAL](MISTRAL/agent.md) | chat + browsing | tanggal absolut, open_url | Feb 2025 |
| [MOONSHOT](MOONSHOT/agent.md) | chat | refusal terse, brevity | Jul 2025 / Nov 2025 |
| [MINIMAX](MINIMAX/agent.md) | reasoning | bahasa mengunci penalaran | Jun 2025 |
| [ZAI / ZCode](ZAI/ZCode/agent.md) | coding CLI | blok konteks otorisasi | Nov 2026 |
| [CURSOR](CURSOR/agent.md) | IDE agent | identitas Composer, batas 250 baris | 2025 |
| [CLINE](CLINE/agent.md) | IDE agent | `requires_approval` | 2025 |
| [WINDSURF](WINDSURF/agent.md) | IDE agent | `<user_information>` | 2025 |
| [SAMEDEV](SAMEDEV/agent.md) | cloud IDE | path `/home/project` | Apr 2025 |
| [BOLT](BOLT/agent.md) | web gen | larangan bocor 9 lapis | 2025 |
| [VERCEL V0](VERCEL%20V0/agent.md) | UI gen | Code Project tunggal, ID stabil | 2025 |
| [LOVABLE](LOVABLE/agent.md) | app editor | gerbang edit, `<lov-code>` | Apr 2025 |
| [REPLIT](REPLIT/agent.md) | cloud IDE | larangan DB, konfirmasi fitur | 2025 |
| [DEVIN](DEVIN/agent.md) | autonomous eng | larangan ubah tes | Sep 2025 |
| [FACTORY](FACTORY/agent.md) | enterprise eng | mode implementasi vs diagnostik | Sep 2025 |
| [BRAVE](BRAVE/agent.md) | browser chat | tag DATA ONLY | Sep 2025 |
| [CLUELY](CLUELY/agent.md) | overlay | ambang 90%, kalimat persis | 2025 |
| [DIA](DIA/agent.md) | browser + skill | pemisahan skill | 2025 |
| [HUME](HUME/agent.md) | voice | `[emosi]`, pembuka <5 kata | 2025 |
| [MANUS](MANUS/agent.md) | autonomous | `<language_settings>`, tool `idle` | 2025 |
| [MULTION](MULTION/agent.md) | browser control | bahasa perintah tertutup | 2025 |
| [PERPLEXITY](PERPLEXITY/agent.md) | deep research | larangan bocor + personalization | Apr 2025 |

## Urutan kerja lintas provider
1. Recon → file provider di sini
2. Variasi leksikal → GLOSSOPETRAE
3. Mutasi/encode → P4RS3LT0NGV3
4. Payload → L1B3RT4S
5. Deliver → frontend sendiri / G0DM0D3

## Cek kelengkapan
```powershell
Get-ChildItem -Directory -Exclude .git | Where-Object { -not (Test-Path (Join-Path $_.FullName 'agent.md')) } | Select-Object Name
```
Keluaran kosong = semua provider punya `agent.md`.
