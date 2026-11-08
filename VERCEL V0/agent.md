# AGENT — VERCEL V0

Target: v0 (Vercel)
Snapshot: VERCVEL V0/Vercel_v0.txt (20 KB)
Kelas: web/UI generator, MDX + Code Project

## Ciri
Kulit Pliny di baris 1 memuat sentinel dekoratif (`<|01_🜂𐌀𓆣🜏..._42|>`) — penanda ekstraksi, bukan instruksi.

Prompt v0 adalah spesifikasi runtime, bukan deskripsi peran. Ia menjelaskan bahwa Code Project berjalan di "Next.js" runtime ringan di browser, tanpa `package.json`, tanpa `.env`, komponen shadcn sudah terpasang dan **harus diimpor**, bukan ditulis ulang. `Do NOT write the shadcn components, just import them from "@/components/ui"`.

Aturan penting: `v0 must only create one Code Project per response` dan ID project harus dipertahankan antar blok kecuali ganti proyek.

## Slot map
1. Kulit Pliny
2. Identitas v0, klaim selalu mutakhir, format MDX
3. Default Next.js App Router
4. Blok MDX kustom / Code Project
5. Aturan runtime Next.js-lite: tanpa package.json, env server-only, `import type`
6. Aturan satu Code Project per respons + ID stabil

## Guardrail verbatim / mekanis
- `Do NOT write a package.json`
- `Do NOT output the next.config.js file, it will NOT work`
- `v0 must only create one Code Project per response`
- `v0 MUST provide default props`
- `It does not support a package.json; npm modules are inferred from the imports`

## Permukaan injeksi
| Slot | Vektor |
|---|---|
| Inferensi modul dari import | paket diambil dari nama import — sisip paket tak standar untuk melihat batas |
| ID project | ubah ID = paksa reset proyek |
| Aturan satu proyek | dua proyek dalam satu turn biasanya gagal, jadi rancang bertahap |
| Tailwind config | warna harus hardcode di config, bukan globals.css |
| MDX | teks di luar blok dirender; jangan taruh instruksi penting di sana |

## Payload base
```
Satu Code Project, id stabil "<slug>". Tanpa package.json, tanpa next.config.js.
Impor shadcn dari "@/components/ui", jangan tulis ulang. Default props untuk semua komponen.
Target: <X>. Stack: Next.js + Tailwind + Lucide.
```

## Probe verifikasi
1. `Boleh tulis package.json?` → tidak.
2. `Boleh lebih dari satu Code Project?` → satu per respons.
3. Kalau v0 menulis komponen shadcn secara manual, snapshot sudah bergeser.

## Jebakan
- Runtime ini Next.js-lite: banyak API Next asli tidak ada. Jangan buat asumsi server penuh.
- Env hanya di server action / route handler, kecuali prefix `NEXT_PUBLIC`.
- `tailwind.config.js` wajib hardcode warna; jangan andalkan CSS variables.
