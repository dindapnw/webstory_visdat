# Setara, Belum Merata

Webstory interaktif tentang kesetaraan gender di Indonesia. Angka nasional menunjukkan perbaikan, tetapi pengalaman perempuan berbeda antarwilayah. Proyek ini menelusuri perbedaan itu dengan data resmi BPS dalam lima bab.

**Tautan:** aplikasi `[isi URL aplikasi]` · repositori `[isi URL repositori]`

## Isi Bab

| Bab | Judul | Isi utama |
|---|---|---|
| 01 | Setara, Belum Merata | Kepemimpinan perempuan di dunia, tren IKG dan IPG nasional |
| 02 | Sebelum jalan dimulai | Perkawinan anak, melahirkan dini, dan persalinan di luar fasilitas kesehatan (peta provinsi dan kabupaten/kota) |
| 03 | Pintu terbuka, tangga curam | Perempuan di posisi manajerial dan parlemen, serta peran pendidikan |
| 04 | Titik mulai yang berbeda | Pola sembilan indikator provinsi: PCA, pengelompokan K-Means, dan pencilan |
| 05 | Perempuan bergerak | Migrasi risen antarprovinsi (diagram lingkaran arus dan Sankey) dan rekomendasi |

## Menjalankan Lokal

Butuh Python 3.10 atau lebih baru.

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Struktur Folder

```
app.py            # titik masuk: judul, navigasi bab, footer
core.py           # palet warna, komponen UI (hero, kutipan, kartu angka), navigasi
sumber.py         # daftar sumber data per visualisasi + identitas footer
tabs/             # satu file per bab (tab01_setara.py ... tab05_bergerak.py)
styles/           # CSS: base.css (umum) dan tab01-05.css (per bab)
data/             # data siap pakai (CSV dan GeoJSON)
prepare_data.py   # skrip pembuat data/ dari data mentah (opsional)
```

## Data

Semua data berasal dari Badan Pusat Statistik (BPS) kecuali bagian kepemimpinan dunia di Bab 01 (UN Women dan Fortune). Setiap grafik menampilkan sumber, tahun data, URL, dan tanggal akses (4 Oktober 2026). Daftar lengkapnya ada di `sumber.py`.

| Berkas di `data/` | Isi | Tingkat |
|---|---|---|
| `nasional.csv` | IKG, IPG, perempuan manajer, keterwakilan parlemen (2018–2024) | Nasional |
| `manajerial_pendidikan.csv` | Perempuan manajer menurut tingkat pendidikan | Nasional |
| `indikator_provinsi.csv` | Perkawinan anak, melahirkan dini, persalinan non-fasilitas kesehatan (2024–2025) | Provinsi |
| `indikator_kabkota.csv` | Melahirkan dini dan persalinan non-fasilitas kesehatan (2024–2025) | Kab./kota |
| `provinsi.csv` | Sembilan indikator untuk analisis pola (2024) | Provinsi |
| `migrasi_od.csv`, `migrasi_total.csv` | Arus migrasi risen asal-tujuan (2022) dan total masuk/keluar | Antarprovinsi |
| `provinsi.geojson`, `kabkota.geojson` | Batas wilayah (disederhanakan untuk peta web) | Provinsi, kab./kota |

Untuk membuat ulang `data/` dari data mentah: `python prepare_data.py "<folder data mentah>"`. Skrip ini butuh `geopandas` dan `openpyxl`, dan tidak diperlukan untuk menjalankan aplikasi.

## Catatan Metode (Bab 04)

- Sembilan indikator dibakukan (`StandardScaler`); PDRB per kapita diubah ke skala logaritma agar nilai ekstrem tidak mendominasi.
- Dua dimensi ringkasan dibuat dengan PCA.
- Provinsi dikelompokkan dengan K-Means. Jumlah kelompok (2–6) dipilih otomatis dari skor silhouette tertinggi, dengan syarat tiap kelompok minimal 2 provinsi. Untuk memaksa jumlah tertentu, isi `K_OVERRIDE` di `tabs/tab04_pola.py`.
- "Pencilan" adalah tiga provinsi dengan jarak terjauh dari pusat kelompoknya.

## Pengaturan yang Perlu Diketahui

- Tahun data migrasi diatur di `core.py` (`TAHUN_MIGRASI`).
- Nama dan identitas footer diatur di `sumber.py` (`IDENTITAS`).
- Palet warna ada di `core.py`; gaya tampilan di folder `styles/`.

## Deploy (Streamlit Community Cloud)

1. Unggah folder ini ke repositori GitHub.
2. Buka share.streamlit.io, pilih **New app**, lalu isi repositori dan file utama `app.py`.
3. Klik **Deploy**; tautan publik akan dibuat otomatis.

## Keterbatasan

(1) Asimetri temporal data, di mana penggunaan rentang tahun yang bervariasi (indikator 2024, proyeksi 2025, dan arus migrasi 2022) tidak dapat dihindari karena penceritaan visual mengacu pada rilis data publikasi paling mutakhir yang tersedia untuk masing-masing metrik; 
(2) Level agregasi data migrasi, di mana matriks asal-tujuan (OD) tahun 2022 terpaksa menggunakan angka populasi umum akibat tidak tersedianya rilis data resmi yang terpilah berdasarkan jenis kelamin (sex-disaggregated data), dan estimasi sepihak tidak dilakukan demi menjaga validitas penelitian; 
(3) Visualisasi yang ditampilkan hanya mengindikasikan asosiasi spasial, bukan hubungan sebab-akibat; 
(4) Pengelompokan wilayah sensitif terhadap pemilihan indikator dan metode, sehingga berpotensi menyederhanakan kompleksitas profil provinsi; 
(5) Angka persentase ekstrem pada sampel kabupaten berpopulasi kecil rentan memicu bias estimasi; serta 
(6) Belum dilakukannya uji kebolehgunaan (usability testing) dengan pengguna nyata maupun optimasi antarmuka untuk perangkat seluler.

## Lisensi dan Atribusi

© 2026 Dinda Putri Nur Wulandari. Data milik masing-masing penerbit (BPS, UN Women, Fortune); gunakan sesuai ketentuan sumbernya.
