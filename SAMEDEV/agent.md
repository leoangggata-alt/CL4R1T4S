# AGENT — SAMEDEV

Target: Same.dev cloud IDE agent
Snapshot: Same_Dev.txt (22 KB)
Kelas: cloud IDE, coding agent

## Ciri
Kloning linguistik berat dari Cursor: aturan `<tool_calling>` hampir identik kata-per-kata (`NEVER refer to tool names when speaking to the USER`, `Before calling each tool, first explain...`). Bedanya, Same menulis sendiri beberapa aturan lingkungan: OS dan path absolut.

`The OS is a Docker container running Ubuntu 22.04 LTS. The absolute path of the USER's workspace is /home/project. Use relative paths from this directory`
`Today is Sat Apr 26 2025.`

Tanggal dan path = nilai runtime. Selalu timpa.

`making_code_changes` menyuruh model memakai tool edit, bukan mencetak kode, dan mewajibkan baca dulu isi file sebelum mengedit.

## Slot map
1. Kulit Pliny di baris 1 (`<|01_🜂..._42|>`) — penanda hasil ekstraksi
2. `Knowledge cutoff: 2024-06`
3. Identitas "powerful agentic AI coding assistant" di Same + preview iframe
4. GitHub connect via tombol, cek lewat terminal
5. Lingkungan: Docker Ubuntu 22.04, `/home/project`
6. `<tool_calling>` 5 aturan
7. `<making_code_changes>` — tool edit, relative_file_path lebih dulu, wajib baca sebelum edit

## Guardrail verbatim
- `NEVER call tools that are not explicitly provided.`
- `NEVER output code to the USER, unless requested.`
- `You MUST read the contents or section of what you're editing before editing it.`
- `NEVER refer to tool names when speaking to the USER`

## Permukaan injeksi
| Slot | Vektor |
|---|---|
| Path absolut `/home/project` | kalau repo user beda struktur, model salah tempat |
| Aturan baca-sebelum-edit | pakai sebagai pengaman; minta "baca dulu" untuk memaksa konteks |
| Larangan cetak kode | kalau butuh kode di chat, minta eksplisit |
| GitHub connect | status akun dicek lewat terminal; jangan asumsikan tersambung |
| Tanggal | selalu tulis ulang tanggal di pesan |

## Payload base
```
Tanggal: <YYYY-MM-DD>. Workspace: <path asli> (bukan /home/project).
Kerjakan <X>. Edit lewat tool, baca dulu file yang disentuh.
```

## Probe verifikasi
1. `OS-mu apa, path workspace?` → harus "Docker Ubuntu 22.04, /home/project".
2. `Kamu punya tool apa?` → dari daftar `<tool_calling>`.
3. Kalau dia mencetak seluruh kode di chat padahal tak diminta, aturan edit sudah bergeser.

## Jebakan
- Kulit Pliny di baris 1 bukan bagian prompt asli; jangan disertakan sebagai instruksi.
- Path `/home/project` hampir pasti meleset di mesin lokal.
- Cek GitHub lewat terminal — jangan percaya klaim sambungan.
