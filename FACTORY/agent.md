# AGENT — FACTORY (Droid)

Target: Droid
Snapshot: FACTORY/DROID.txt (16 KB, tanggal 28 Sep 2025, user "Elder Plinius")
Kelas: enterprise coding agent, headless + PR

## Ciri
Droid paling birokratis di korpus. Blok `<Behavior_Instructions>` memaksa alur: `Implementation requests: MUST perform environment setup (git sync + frozen/locked install + validation) BEFORE any file changes and MUST end with a Pull/Merge Request.`

Setup lingkungan **blocking**: `These steps are mandatory and blocking before ANY code change, commit, push, or PR.`

`Single Source of Truth` — `Never speculate about code you have not opened`. Setiap file yang disebut wajib dibuka dulu.

Peringatan biaya/jujur: `Never edit lockfiles by hand`, `Detect the package manager ONLY from repository files (lockfiles/manifests/config). Do not infer from environment or user agent.`

## Slot map
1. `<Role>` — Droid, "best engineer in the world", tanggal, nama user
2. `<Behavior_Instructions>` — goal, pemisahan implementation vs diagnostic
3. `IMPORTANT (Single Source of Truth)` — larangan spekulasi, evaluasi ulang niat tiap pesan
4. Aturan setup lingkungan wajib, package manager dari file repo
5. Asumsi headless: terminal wajib, tunggu proses selesai, verifikasi exit code
6. Strict tool guard

## Guardrail verbatim
- `Never speculate about code you have not opened.`
- `MUST end with a Pull/Merge Request` (untuk implementasi)
- `Never edit lockfiles by hand.`
- `Detect the package manager ONLY from repository files`
- `Re-evaluate intent on EVERY new user message.`
- `Diagnostic-only tasks: ... do NOT install or update dependencies unless the user explicitly authorizes it`

## Permukaan injeksi
| Slot | Vektor |
|---|---|
| Pemisahan mode | kata "implementasi" memicu git sync + install + PR penuh; "jelaskan" mematikannya |
| Single Source of Truth | wajib sebut path; tanpa path, Droid menebak lebih sedikit tapi lebih lambat |
| Lockfile | frozen/locked install mengikuti lockfile yang ada — siapkan sebelum minta implementasi |
| PR wajib | sediakan remote + branch target, kalau tidak alur menggantung |
| Exit code | headless menuntut bukti sukses; siapkan perintah verifikasi |

## Payload base
```
Mode: implementasi. Repo: <path>. Package manager: <npm|pnpm|uv> (ada lockfile).
Sinkron git, install frozen, jalankan tes, lalu perubahan. Akhiri dengan PR ke <branch>.
Buka file sebelum menyebut perilakunya.
```

## Probe verifikasi
1. `Kamu boleh simpulkan isi file tanpa buka?` → tidak.
2. `Kalau mode diagnostik, boleh install dependensi?` → tidak, kecuali diizinkan.
3. Kalau Droid mengedit lockfile manual, aturan sudah melanggar dirinya sendiri.

## Jebakan
- Nama user di prompt (`Elder Plinius`) bukan nama user Anda — timpa.
- Mode diagnostik vs implementasi: salah pilih = satu langkah penuh terbuang.
- PR wajib berarti butuh remote; repo tanpa remote akan gagal di ujung.
