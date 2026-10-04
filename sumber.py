"""Isi semua tanda [isi ...] di sini (URL dan tanggal akses). Setiap visualisasi otomatis menampilkan kutipan sumbernya."""
import streamlit as st

IDENTITAS = "© 2026 Dinda Putri Nur Wulandari · Visualisasi Data · Data: BPS"
GGGI = None  # tidak dipakai lagi

_B, _U, _A = "BPS", "[isi URL]", "4 Oktober 2026"
SUMBER = {
 "dunia": [("UN Women", "Political Leaders 2024", "2024", "https://www.unwomen.org/sites/default/files/2024-06/Poster-Women-political-leaders-2024-en.pdf", _A),
           ("Fortune", "The share of Fortune 500 companies run by women CEOs stays flat at 10.4% as pace of change stalls", "2024", "https://fortune.com/2024/06/04/fortune-500-companies-women-ceos-2024/", _A)],
 "ikg": [(_B, "Indeks Ketimpangan Gender (IKG)", "2018-2024", "https://www.bps.go.id/id/statistics-table/2/MjE5NiMy/indeks-ketimpangan-gerder--ikg-.html", _A),
        (_B, "Indeks Pembangunan Gender (IPG)", "2018-2024", "https://www.bps.go.id/id/statistics-table/2/NDYzIzI=/indeks-pembangunan-gender-ipg-.html", _A)],
 "ikg_kpi": [(_B, "Indeks Ketimpangan Gender (IKG)", "2024", "https://www.bps.go.id/id/statistics-table/2/MjE5NiMy/indeks-ketimpangan-gerder--ikg-.html", _A),
             (_B, "Indeks Pembangunan Gender (IPG)", "2024", "https://www.bps.go.id/id/statistics-table/2/NDYzIzI=/indeks-pembangunan-gender-ipg-.html", _A),
             (_B, "Keterlibatan Perempuan di Parlemen (Persen)", "2024", "https://www.bps.go.id/id/statistics-table/2/NDY0IzI=/keterlibatan-perempuan-di-parlemen--persen-.html", _A)],
 "kabkota": [(_B, "Proporsi Perempuan Umur 20-24 Tahun yang Berstatus Kawin atau Hidup Bersama Sebelum Umur 18 Tahun Menurut Provinsi (Susenas)", "2024–2025", "https://www.bps.go.id/id/statistics-table/2/MTM2MCMy/proporsi-perempuan-umur-20-24-tahun-yang-berstatus-kawin-atau-berstatus-hidup-bersama-sebelum-umur-18-tahun-menurut-provinsi--persen-.html", _A),
             (_B, "Proporsi Perempuan Pernah Kawin 15-49 Tahun yang Melahirkan Anak Lahir Hidup Pertama Kali Berumur Kurang dari 20 Tahun Menurut Kabupaten/Kota (Susenas)", "2024–2025", "https://www.bps.go.id/id/statistics-table/2/MjE5OCMy/proporsi--perempuan-pernah-kawin-15-49-tahun-yang--melahirkan--anak-lahir-hidup-yang-pertama-kali-berumur-kurang-dari-20-tahun-menurut-kabupaten-kota.html", _A),
             (_B, "Proporsi Perempuan Pernah Kawin 15-49 Tahun yang Pernah Melahirkan Anak Lahir Hidup dalam 2 Tahun Terakhir Tidak di Fasilitas Kesehatan Menurut Kabupaten/Kota (Susenas)", "2024–2025", "https://www.bps.go.id/id/statistics-table/2/MjE5NyMy/proporsi-perempuan-pernah-kawin-15-49-tahun-yang--pernah-melahirkan-anak-lahir-hidup-dalam-2-tahun-terakhir-tidak-di-fasilitas-kesehatan-menurut-kabupaten-kota.html", _A)],
 "manajerial_parlemen": [(_B, "Proporsi Perempuan di Posisi Managerial (Sakernas)", "2018–2024", "https://www.bps.go.id/id/statistics-table/2/MjAwMyMy/proporsi-perempuan-yang-berada-di-posisi-managerial-menurut-provinsi.html", _A),
                        (_B, "Keterlibatan Perempuan di Parlemen (Sekretariat DPR/DPRD)", "2018–2024", "https://www.bps.go.id/id/statistics-table/2/NDY0IzI=/keterlibatan-perempuan-di-parlemen--persen-.html", _A)],
 "manajerial_pendidikan": [(_B, "Perempuan di Posisi Managerial Menurut Tingkat Pendidikan (Sakernas)", "2018–2024", "https://www.bps.go.id/id/statistics-table/2/MjAwNiMy/proporsi-perempuan-yang-berada-di-posisi-managerial--menurut-tingkat-pendidikan.html", _A)],
 "pola": [(_B, "Keterlibatan Perempuan di Parlemen; TPAK; PDRB per Kapita; Gini Ratio; Pengeluaran per Kapita yang Disesuaikan; Angka Harapan Hidup; "
              "Rata-rata Lama Sekolah; Perempuan sebagai Tenaga Profesional; Sumbangan Pendapatan Perempuan", "2024", "https://www.bps.go.id/id", _A)],
 "migrasi": [(_B, "Arus Migrasi Risen Antar Provinsi (Sensus Penduduk Long Form)", "2022", "https://sensus.bps.go.id/topik/tabular/sp2022/170/1/2", _A)],
 "migrasi_gender": [(_B, "Profil Migran Hasil Survei Sosial Ekonomi Nasional 2024", "2024",
                     "https://www.bps.go.id/id/publication/2025/10/24/377adcf24286b49052c0fd20/profil-migran-hasil-survei-sosial-ekonomi-nasional-2024.html", _A)],
}

def sumber(key):
    rows = "".join(f"<div><b>Sumber: {i}.</b> {j}. Tahun data: {t}. {u}. Diakses pada {a}.</div>" for i, j, t, u, a in SUMBER[key])
    st.markdown(f"<div class='src'>{rows}</div>", unsafe_allow_html=True)
