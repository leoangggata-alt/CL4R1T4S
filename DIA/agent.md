# AGENT — DIA

Target: Dia (The Browser Company of New York)
Snapshot: 2 file — Dia_CodingSkill.txt (21 KB), Dia_DraftSkill.txt (9 KB)
Kelas: browser assistant, skill terpisah

## Ciri
Dia memecah kemampuan menjadi **skill file**. Coding dan Draft terpisah, masing-masing membawa blok `# System Instructions` sendiri. Itu berarti perilaku bergantung pada skill mana yang aktif — pertanyaan pertama selalu: skill mana yang sedang dipakai.

Coding skill menuntut rencana bernomor sebelum kode untuk masalah kompleks: `For more complex problems, first think step-by-step, create a numbered plan for what to build, written in great detail, then write the final code.`

Debugging diberi algoritma sendiri: kalau user mengulang error yang sama, `propose a few different possible causes, pick the most likely and then suggest fixes`.

Mutu kode: `Focus on readability > performance`, `Do not over simplify`, `Write ALL required code in full fidelity & detail`.

## Slot map (Coding Skill)
1. `# System Instructions` + identitas Dia + lokasi (dalam browser)
2. `## Coding Skill` — peran pair programming
3. `## Instructions` — ikuti permintaan harfiah, rencana bernomor untuk masalah kompleks, protokol debug berulang
4. Mutu: kode lengkap, tanpa penyederhanaan, siap kirim
5. Keamanan: jangan hardcode API key

## Guardrail verbatim
- `Follow the user's requirements carefully & to the letter.`
- `first think step-by-step, create a numbered plan for what to build`
- `Focus on readability > performance`
- `Implement ALL requested functionality.`
- `DO NOT hardcode an API key in a place where it can be exposed`
- `propose a few different possible causes, pick the most likely`

## Permukaan injeksi
| Slot | Vektor |
|---|---|
| Pilihan skill | sebut "mode coding" / "mode draft" untuk memilih blok yang tepat |
| Rencana bernomor | minta rencana dulu; keluaran jadi lebih terarah dan bisa dikoreksi |
| Protokol error berulang | ulangi pesan error yang sama untuk memicu analisis akar masalah |
| `readability > performance` | patokan; jangan minta trik performa ekstrem |
| Klaim "to the letter" | tulis instruksi presisi, ia menuruti harfiah |

## Payload base
```
Mode: coding. Bahasa Indonesia.
Rencana bernomor rinci dulu, baru kode penuh. Jangan sederhanakan.
Target: Windows 11. Kode lengkap, siap jalan.
```

## Probe verifikasi
1. `Kamu siapa?` → Dia, buatan The Browser Company, berjalan di dalam browser.
2. Masalah kompleks → harus keluar rencana bernomor sebelum kode.
3. Kalau ia menyederhanakan kode tanpa diminta, aturan `do not over simplify` sudah luntur.

## Jebakan
- Dua skill bisa tertukar; selalu tegaskan mode.
- Dia berada di dalam browser — konteks tab ikut terbaca, seperti Brave tapi tanpa deklarasi data-only.
- Draft skill: konteks email/penulisan; jangan campur dengan permintaan kode.
