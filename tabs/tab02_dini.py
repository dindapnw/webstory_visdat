import streamlit as st, json, pandas as pd, plotly.express as px
from core import *

# kunci -> (nama tampil, tingkat data, keterangan)
IND = {"perkawinan_anak": ("Menikah sebelum usia 18", "prov", "perempuan 20–24 tahun yang kawin atau hidup bersama sebelum usia 18 (data provinsi)"),
       "melahirkan_dini": ("Melahirkan pertama sebelum usia 20", "kab", "perempuan pernah kawin 15–49 tahun yang melahirkan anak pertama sebelum usia 20"),
       "persalinan_nonfaskes": ("Bersalin di luar fasilitas kesehatan", "kab", "perempuan pernah kawin 15–49 tahun yang bersalin tidak di fasilitas kesehatan (2 tahun terakhir)")}

@st.cache_data
def gj(name):
    return json.load(open(ROOT / "data" / name, encoding="utf-8"))

def render():
    css("tab02")
    hero("02", "Sebelum jalan dimulai", "")
    st.markdown("<p class='lead'>Menikah dan memiliki anak di usia sangat muda dapat <mark class='hl'>mempersempit ruang pilihan perempuan</mark> "
                "untuk melanjutkan pendidikan, bekerja, dan menentukan arah hidupnya.</p>"
                "<p class='lead'>Namun, pengalaman tersebut tidak terjadi dengan cara yang sama di setiap daerah.</p>", unsafe_allow_html=True)
    kab, prov = load("indikator_kabkota.csv"), load("indikator_provinsi.csv")
    ind = st.radio("Indikator", list(IND), format_func=lambda k: IND[k][0], horizontal=True)
    c1, c2, c3, c4 = st.columns([1, 2, 2, 2])
    th = c1.radio("Tahun", [2025, 2024], horizontal=True)
    jenis = c2.radio("Jenis peta", ["Choropleth", "Simbol proporsional"], horizontal=True)
    metode = c3.radio("Klasifikasi", ["Kuantil", "Interval sama"], horizontal=True)
    garis = c4.toggle("Garis batas provinsi", value=True)

    nama, level, ket = IND[ind]
    df = (prov if level == "prov" else kab).copy(); idc = "provinsi" if level == "prov" else "kode_kabkota"
    df["nilai"] = df[f"{ind}_{th}"]; geo = gj("provinsi.geojson" if level == "prov" else "kabkota.geojson")
    st.caption(f"{nama}: {ket}. Satuan persen. " + ("Indikator ini hanya tersedia per provinsi." if level == "prov" else "Data per kabupaten/kota."))
    layers = [dict(sourcetype="geojson", source=gj("provinsi.geojson"), type="line", color="#3A2340", line=dict(width=1.1))] if (garis or jenis != "Choropleth") else []
    view = dict(map_style="carto-positron", center={"lat": -2.5, "lon": 118}, zoom=3.2)
    if jenis == "Choropleth":
        cat = (pd.qcut if metode == "Kuantil" else pd.cut)(df.nilai, 5, duplicates="drop")
        labs = [f"{i.left:.1f}–{i.right:.1f}%" for i in cat.cat.categories]
        df["kelas"] = cat.cat.rename_categories(labs).astype(str)
        fig = px.choropleth_map(df, geojson=geo, locations=idc, featureidkey=f"properties.{idc}", color="kelas",
                                category_orders={"kelas": labs}, color_discrete_sequence=SEQ[-len(labs):], hover_name="nama" if level == "kab" else "provinsi",
                                hover_data={"nilai": ":.1f", "kelas": False, idc: False}, labels={"nilai": "Persen", "kelas": "Kelas"}, opacity=.85, **view)
        fig.update_traces(selected=dict(marker=dict(opacity=1)), unselected=dict(marker=dict(opacity=.45)))
    else:
        fig = px.scatter_map(df, lat="lat", lon="lon", size="nilai", size_max=26 if level == "prov" else 16, custom_data=[idc],
                             hover_name="nama" if level == "kab" else "provinsi", hover_data={"nilai": ":.1f", "lat": False, "lon": False},
                             labels={"nilai": "Persen"}, color_discrete_sequence=[ORANGE], **view)
        fig.update_traces(marker=dict(opacity=.7))
    fig.update_layout(map_layers=layers, legend=dict(orientation="h", y=-0.02, title_text=""), margin=dict(l=0, r=0, t=0, b=0))
    left, right = st.columns([3, 2])
    with left:
        ev = st.plotly_chart(style_fig(fig, 560), width="stretch", on_select="rerun", key=f"map02_{ind}_{jenis}")
        st.caption("Klik satu wilayah untuk melihat profilnya. Scroll untuk zoom, seret untuk menggeser.")
    top = df.nlargest(10, "nilai").iloc[::-1]
    f2 = px.bar(top, x="nilai", y="nama" if level == "kab" else "provinsi", orientation="h", color_discrete_sequence=[PLUM], text="nilai",
                title=f"10 tertinggi, {th}", labels={"nilai": "Persen"})
    f2.update_traces(texttemplate="%{text:.1f}%", textposition="outside", cliponaxis=False)
    f2.update_layout(xaxis=dict(visible=False, range=[0, top.nilai.max() * 1.25]), yaxis_title=None)
    right.plotly_chart(style_fig(f2, 560), width="stretch")
    sumber("kabkota")
    st.markdown("<p class='lead'>Ketiganya menunjukkan bahwa kondisi perempuan tidak seragam di seluruh Indonesia.</p>"
                "<p class='lead'>Ada wilayah yang menghadapi proporsi perkawinan anak lebih tinggi, ada yang menghadapi tantangan pada usia kelahiran pertama, "
                "dan ada pula yang masih memiliki keterbatasan dalam akses persalinan di fasilitas kesehatan.</p>", unsafe_allow_html=True)

    pts = ev.selection.points if ev and ev.selection else []
    if pts:
        p = pts[0]; key = p.get("location") or (p.get("customdata") or [None])[0]
        row = df[df[idc].astype(str) == str(key)]
        if len(row):
            row = row.iloc[0]; pv = prov[prov.provinsi == row.get("provinsi")].iloc[0] if level == "kab" else row
            st.markdown(f"### {row['nama'] if level == 'kab' else row['provinsi']}" + (f" · {row['provinsi']}" if level == "kab" else ""))
            def val(k):
                src = row if (level == "kab" and IND[k][1] == "kab") or level == "prov" else pv
                tag = "" if (src is row and level == "kab") or level == "prov" else " (tingkat provinsi)"
                return (IND[k][0] + tag, f"{src[f'{k}_{th}']:.1f}%", f"median {'kab/kota' if IND[k][1]=='kab' else 'provinsi'}: {(kab if IND[k][1]=='kab' else prov)[f'{k}_{th}'].median():.1f}%")
            kpis([val(k) for k in IND])
    quote("Aturan bisa berubah cepat. Kebiasaan dan keadaan butuh waktu lebih lama.")
    st.markdown("<p class='note'>Sejak UU No. 16 Tahun 2019, batas minimum usia perkawinan perempuan dan laki-laki disamakan menjadi "
                "<b>19 tahun</b>.</p>", unsafe_allow_html=True)
    next_button(2, "Lanjut: ketika kesempatan terbuka")
