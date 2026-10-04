import streamlit as st, plotly.graph_objects as go, plotly.express as px
from core import *

def render():
    css("tab03")
    hero("03", "Pintu terbuka, tangga curam", "Setelah punya akses, seberapa jauh perempuan bisa naik?")
    nas = load("nasional.csv")
    th = st.select_slider("Pilih tahun", options=list(nas.tahun), value=nas.tahun.iloc[-1])
    last = nas[nas.tahun == th].iloc[0]
    fig = go.Figure(go.Bar(y=["Parlemen", "Manajerial"], x=[last.parlemen, last.manajerial], orientation="h",
                           marker_color=[ORANGE, TEAL], text=[f"{last.parlemen:.1f}%", f"{last.manajerial:.1f}%"],
                           textposition="outside", textfont=dict(size=18)))
    fig.update_layout(title="Porsi perempuan: ruang profesional vs ruang politik",
                      xaxis=dict(range=[0, 60], showgrid=False, title="% perempuan"))
    st.plotly_chart(style_fig(fig, 300), width="stretch")
    sumber("manajerial_parlemen")
    quote("Angkanya menunjukkan bahwa perempuan sudah hadir dalam ruang profesional maupun publik.<br>"
          "Namun, semakin dekat kita pada ruang pengambilan keputusan, proporsinya masih lebih kecil.")
    st.markdown("<p class='lead'>Salah satu pintu yang sering dikaitkan dengan peluang perempuan adalah pendidikan.</p>"
                "<p class='lead'>Tetapi apakah semakin tinggi pendidikan selalu diikuti oleh semakin besar keterwakilan perempuan dalam posisi manajerial?</p>", unsafe_allow_html=True)
    st.markdown("### Apakah pendidikan ikut membedakan peluang?")
    e = load("manajerial_pendidikan.csv"); yrs = sorted(e.tahun.unique())
    a, b = st.select_slider("Periode", options=yrs, value=(yrs[0], yrs[-1]))
    st.caption("Geser kedua ujung untuk memilih periode yang ingin dilihat.")
    e = e[(e.tahun >= a) & (e.tahun <= b)]
    f2 = go.Figure()
    for c, (lvl, d) in zip([TEAL, ORANGE, SKY, "#D55E00", "#CC79A7", CHAR], e.groupby("pendidikan", sort=False)):
        f2.add_trace(go.Scatter(x=d.tahun, y=d.persen, mode="lines+markers", name=lvl, line=dict(color=c, width=3), marker=dict(size=8)))
    f2.update_layout(title=f"Perempuan manajer menurut pendidikan, {a}–{b}" if a != b else f"Perempuan manajer menurut pendidikan, {a}",
                     hovermode="x unified", xaxis=dict(dtick=1, title=None), yaxis=dict(title="% perempuan", gridcolor="#e3dde4"))
    st.plotly_chart(style_fig(f2, 420).update_layout(legend=dict(orientation="v", x=1.02, y=1, xanchor="left"), margin=dict(l=10, r=10, t=44, b=10)), width="stretch")
    sumber("manajerial_pendidikan")
    st.markdown("<p class='lead'>Pendidikan memang penting. Tetapi posisi perempuan tidak berdiri sendiri.</p>"
                "<p class='lead'>Kesehatan, kondisi ekonomi, partisipasi kerja, hingga keterwakilan di ruang publik juga ikut menggambarkan bagaimana perempuan menjalani kehidupannya.</p>"
                "<p class='lead'>Lalu, bagaimana jika <mark class='hl'>semua aspek tersebut kita lihat secara bersamaan</mark>?</p>", unsafe_allow_html=True)
    next_button(3, "Lihat semuanya sekaligus")
