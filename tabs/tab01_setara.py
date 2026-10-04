import streamlit as st, plotly.graph_objects as go
from core import *

def prolog():
    st.markdown("<div class='prolog'><p>Dibanding masa lalu, perempuan kini memiliki ruang yang jauh lebih luas untuk "
                "<mark class='hl'>bersekolah, bekerja, dan menyuarakan pendapat</mark>.</p>"
                "<p>Sekilas, kemajuan ini membuat kesetaraan gender terasa semakin dekat.</p></div>",
                unsafe_allow_html=True)
    st.markdown("<div class='prolog r'><p>Namun, ketika kita melihat siapa yang berada di ruang pengambilan keputusan, gambarnya belum sepenuhnya berubah.</p>"
                "<p><mark class='hl'>Perempuan masih lebih sedikit hadir di posisi kepemimpinan.</mark></p></div>",
                unsafe_allow_html=True)
    kpis([("Negara yang dipimpin perempuan", "29 dari 195", "negara yang diakui dunia", 29 / 195 * 100),
          ("Posisi menteri di dunia yang diisi perempuan", "23,3%", "dari seluruh posisi menteri", 23.3),
          ("Perusahaan Fortune 500 dengan CEO Perempuan", "10,4%", "52 dari 500 perusahaan dalam daftar", 10.4)])
    sumber("dunia")
    st.markdown("<div class='prolog'><p>Lalu, apakah kemajuan tersebut berarti kesetaraan sudah tercapai? <mark class='hl'>Belum tentu</mark>.</p>"
                "<p>Kita mungkin sudah bergerak menuju <b>kesetaraan</b>, tetapi kemajuan itu belum dirasakan secara <b>merata</b>.</p>"
                "<p>Perempuan Indonesia masih menghadapi banyak hambatan untuk mendapat kesempatan yang sama. "
                "Apa saja yang menghalangi perempuan untuk memimpin?</p></div>", unsafe_allow_html=True)

def render():
    css("tab01")
    prolog()
    hero("01", "Setara, Belum Merata", "Membaca Jalan Perempuan Menuju Ruang yang Setara di Indonesia")
    d = load("nasional.csv"); last = d.iloc[-1]
    OPT = {"ikg": ("IKG · Ketimpangan", "Indeks Ketimpangan Gender (IKG): makin kecil, makin baik", ".3f"),
           "ipg": ("IPG · Pembangunan", "Indeks Pembangunan Gender (IPG): makin dekat 100, makin setara", ".1f")}
    k = st.radio("Pilih indeks", list(OPT), format_func=lambda x: OPT[x][0], horizontal=True, label_visibility="collapsed")
    label, judul, f = OPT[k]
    fig = go.Figure(go.Scatter(x=d.tahun, y=d[k], mode="lines+markers", line=dict(color=PLUM, width=5),
                               marker=dict(size=11, color=TEAL, line=dict(width=2, color="#fff")),
                               hovertemplate="<b>%{x}</b><br>" + k.upper() + " %{y:" + f + "}<extra></extra>"))
    fig.add_annotation(x=last.tahun, y=last[k], text=f"<b>{last[k]:{f}}</b>", showarrow=False, yshift=24,
                       font=dict(size=19, color=PLUM))
    fig.update_layout(title=judul, hovermode="x unified", yaxis=dict(gridcolor="#e3dde4", title=None),
                      xaxis=dict(title=None, dtick=1))
    st.plotly_chart(style_fig(fig, 420), width="stretch")
    sumber("ikg")
    quote("Angka nasional dapat menunjukkan bahwa kondisi secara keseluruhan membaik. Tetapi angka nasional juga dapat menyembunyikan perbedaan yang terjadi di baliknya.")
    kpis([("IPG (Indeks Pembangunan Gender)", f"{last.ipg:.1f}", f"tahun {int(last.tahun)}", last.ipg),
          ("Perempuan di posisi manajerial", f"{last.manajerial:.1f}%", "dari seluruh manajer", last.manajerial),
          ("Perempuan di parlemen", f"{last.parlemen:.1f}%", "dari seluruh anggota", last.parlemen)])
    sumber("ikg_kpi")
    next_button(1, "Lihat dari mana semuanya bermula")
