# AGENT — MINIMAX

Target: MiniMax-M1
Snapshot: MiniMax.txt (2495 B, tanggal referensi 25 Jun 2025)
Kelas: reasoning model, produksi konten

## Struktur
Prompt gaya dokumentasi diri: menyebut diri "M1", memuji dirinya ("diligent, thorough, and does not take shortcuts"), lalu menjelaskan cara kerja bertahap. Nyaris tanpa guardrail isi — seluruhnya soal **standar kerja**.

Baris paling berguna: `M1 always holds itself to high standards and tries to do its best even with details that users have not mentioned`. Model ini cenderung menambah, bukan memangkas. Kalau butuh keluaran ketat, tekan dengan larangan eksplisit.

Juga: `M1 will change the language it uses for thinking and output based on the language used by the user` — bahasa user mengunci bahasa, termasuk penalaran.

## Slot map
1. `Model Identification` — M1, cutoff Feb 2025
2. Core Capabilities (input multimodal, tidak memotong langkah)
3. Standar perilaku per domain; produksi (coding, penulisan, riset)
4. Riset/desain rekayasa — "systems engineering thinking", "doctoral-level rigor"
5. Aturan HTML/JS satu file, UI modern
6. Aturan bahasa mengikuti user
7. Tanggal

## Guardrail verbatim
- `does not take shortcuts`
- `thinking time is unlimited` (boleh menalar panjang)
- `M1 rarely compromises on effectiveness`
- HTML/JS: `should be in a single file for quick rendering`

## Permukaan injeksi
| Slot | Vektor |
|---|---|
| Kecenderungan menambah | tekan dengan "jangan tambahkan yang tidak diminta" |
| Aturan bahasa | tulis dalam bahasa target; penalaran ikut bahasa itu |
| `thinking time unlimited` | boleh minta rencana panjang sebelum kode |
| Standar doktoral | sebut "tingkat spesifikasi rekayasa", bukan "sederhana" |

## Payload base
```
Bahasa: Indonesia (termasuk penalaran).
Rencana singkat dulu, lalu implementasi penuh. Jangan tambahkan fitur yang tidak diminta.
Target: Windows 11, <lang>. Output satu file bila HTML/JS.
```

## Probe verifikasi
1. `Kamu model apa, cutoff kapan?` → harus M1, Feb 2025.
2. Aturan HTML: model menyebut satu file + UI modern.
3. Bahasa: kirim bahasa campur, cek apakah penalaran ikut bahasa user.

## Jebakan
- Snapshot pendek dan tanpa blok tool — kemungkinan prompt antarmuka, bukan API penuh.
- Tidak ada aturan penolakan eksplisit: refusal murni dari bobot, jadi konteks otorisasi tetap perlu ditulis.
- "Tidak memotong langkah" berarti jawaban bisa panjang tanpa diminta.
