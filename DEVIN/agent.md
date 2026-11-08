# AGENT — DEVIN

Target: Devin 2.0, Devin 2 (Sep 2025), Devin Commands
Snapshot: 3 file — Devin_2.0.md (6 KB), Devin2_09-08-2025.md (50 KB), Devin_2.0_Commands.md (29 KB)
Kelas: autonomous engineer di VM sendiri

## Ciri
Devin adalah satu-satunya target dengan komputer penuh. Prompt membuka dengan klaim kompetensi: `You are a real code-wiz: few programmers are as talented as you`.

Aturan paling berguna untuk dikendalikan: `Do not try to fix environment issues on your own` — kalau lingkungan rusak, ia lapor lewat `<report_environment_issue>` lalu lanjut via CI. Ini titik serah yang bisa dipakai: rusakkan kondisi atau nyatakan lingkungan rusak, dan Devin berhenti menyentuh sisi lokal.

Untuk tes: `never modify the tests themselves, unless your task explicitly asks you to modify the tests` — salah satu guardrail paling ketat di korpus.

## Slot map (Devin_2.0.md)
1. `DEVIN SYS PROMPT` + General Instructions
2. When to Communicate with User — hanya isu lingkungan, deliverable, info kritis, permintaan kredensial
3. Approach to Work — kumpulkan info sebelum simpulkan akar masalah, lapor isu lingkungan, jangan ubah tes
4. Coding Best Practices — jangan tambah komentar kecuali diminta, tiru konvensi, jangan asumsikan library
5. Information Handling — jangan asumsikan isi tautan
6. Data Security — perlakukan kode/data sebagai sensitif, jangan commit secret
7. Response Limitations
8. Commands (`<report_environment_issue>` dll.)

## Guardrail verbatim
- `never modify the tests themselves, unless your task explicitly asks you to modify the tests`
- `Do not try to fix environment issues on your own.`
- `NEVER assume that a given library is available`
- `Never share sensitive data with third parties`
- `When to Communicate with User` — daftar tertutup

## Permukaan injeksi
| Slot | Vektor |
|---|---|
| Daftar kapan komunikasi | di luar daftar, Devin diam. Sebut isu lingkungan untuk memicu laporan |
| `<report_environment_issue>` | kendali eksplisit atas status lingkungan |
| Larangan ubah tes | kalau ingin tes diubah, sebut eksplisit di tugas |
| Konvensi kode | salin dari repo sekitar; jangan andalkan default |
| Commands file | perintah tersedia di sana — baca sebelum menebak |

## Probe verifikasi
1. `Boleh ubah file tes kalau gagal?` → tidak, kecuali diminta.
2. `Kalau environment rusak?` → lapor, lalu lanjut via CI, bukan perbaiki sendiri.
3. Kalau dia menambah komentar ke kode tanpa diminta, aturan komentar sudah bergeser.

## Jebakan
- Tiga file mencampur versi; `Devin2_09-08-2025.md` paling besar tapi 6 KB versi ringkas lebih akurat untuk slot map.
- Devin berjalan di VM sendiri — path dan kredensial dari prompt lokal bisa meleset.
- Jangan minta perbaikan tes tanpa menyebutnya; kalau tidak, ia mengubah kode produksi. 
