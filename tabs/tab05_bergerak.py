import streamlit as st, numpy as np, pandas as pd, plotly.graph_objects as go
from core import *

PAL = [TEAL, ORANGE, SKY, PLUM, "#D55E00", "#CC79A7", "#0072B2", "#8C8C3F"]
REK = [("Cegah sejak dini", "Perkuat pencegahan perkawinan anak dan layanan kesehatan remaja, terutama di wilayah yang angkanya tinggi."),
       ("Buka jalan ke kursi pemimpin", "Dukung perempuan naik ke posisi pengambil keputusan lewat pelatihan, pendampingan, dan aturan kerja yang ramah keluarga."),
       ("Sesuaikan dengan wilayah", "Rancang program berbeda untuk tiap kelompok wilayah, dan buka peluang sekolah dan kerja di daerah asal.")]

def rgba(h, a):
    h = h.lstrip("#"); return f"rgba({int(h[:2],16)},{int(h[2:4],16)},{int(h[4:],16)},{a})"

def arc(a0, a1, r, n=20):
    t = np.linspace(a0, a1, n); return r * np.cos(t), r * np.sin(t)

def bez(p, q, n=24):  # kurva kuadrat dengan titik kontrol di pusat lingkaran
    t = np.linspace(0, 1, n)[:, None]; return (1 - t) ** 2 * np.array(p) + t ** 2 * np.array(q)

def chord(fl):
    nodes = sorted(set(fl.asal) | set(fl.tujuan))
    out, inn = fl.groupby("asal").jumlah.sum(), fl.groupby("tujuan").jumlah.sum()
    tot = {n: out.get(n, 0) + inn.get(n, 0) for n in nodes}
    gap = .04; scale = (2 * np.pi - gap * len(nodes)) / sum(tot.values()); cur, a = {}, 0.
    for n in nodes: cur[n] = a; a += tot[n] * scale + gap
    start = dict(cur); col = {n: PAL[i % len(PAL)] for i, n in enumerate(nodes)}; R = .93; fig = go.Figure()
    for r in fl.sort_values("jumlah", ascending=False).itertuples():
        w = r.jumlah * scale; s0 = cur[r.asal]; cur[r.asal] += w; t0 = cur[r.tujuan]; cur[r.tujuan] += w
        sx, sy = arc(s0, s0 + w, R); tx, ty = arc(t0, t0 + w, R)
        b1 = bez((sx[-1], sy[-1]), (tx[0], ty[0])); b2 = bez((tx[-1], ty[-1]), (sx[0], sy[0]))
        fig.add_trace(go.Scatter(x=np.r_[sx, b1[:, 0], tx, b2[:, 0]], y=np.r_[sy, b1[:, 1], ty, b2[:, 1]], mode="lines", fill="toself",
                                 line=dict(width=.4, color=col[r.asal]), fillcolor=rgba(col[r.asal], .55), hoveron="fills", hoverinfo="text",
                                 text=f"<b>{r.asal} → {r.tujuan}</b><br>{r.jumlah:,} jiwa".replace(",", "."), showlegend=False))
    lab = []
    for n in nodes:
        a0, a1 = start[n], start[n] + tot[n] * scale; ox, oy = arc(a0, a1, 1.0); ix, iy = arc(a1, a0, .95)
        fig.add_trace(go.Scatter(x=np.r_[ox, ix], y=np.r_[oy, iy], mode="lines", fill="toself", fillcolor=col[n], line=dict(width=0), hoveron="fills",
                                 hoverinfo="text", showlegend=False,
                                 text=f"<b>{n}</b><br>Keluar: {int(out.get(n, 0)):,} jiwa<br>Masuk: {int(inn.get(n, 0)):,} jiwa".replace(",", ".")))
        lab.append((n, (a0 + a1) / 2))
    # label ditaruh di dua kolom di luar lingkaran (kiri/kanan) dengan jarak minimal, dihubungkan garis tipis ke busurnya
    gap, lim = .075, -1.15; lx, ly, lt, lp, cx, cy = [], [], [], [], [], []
    for side in (1, -1):
        items = sorted([(1.03 * np.sin(m), n, m) for n, m in lab if (np.cos(m) >= 0) == (side == 1)], reverse=True)
        ys = []
        for y0, _, _ in items: ys.append(min(y0, ys[-1] - gap) if ys else y0)
        for i in range(len(ys) - 1, -1, -1): ys[i] = max(ys[i], lim if i == len(ys) - 1 else ys[i + 1] + gap)
        for (y0, n, m), y in zip(items, ys):
            cx += [1.02 * np.cos(m), side * 1.1, None]; cy += [1.02 * np.sin(m), y, None]
            lx.append(side * 1.12); ly.append(y); lt.append(n); lp.append("middle right" if side == 1 else "middle left")
    fig.add_trace(go.Scatter(x=cx, y=cy, mode="lines", line=dict(width=.8, color="#B8B0A8"), hoverinfo="skip", showlegend=False))
    fig.add_trace(go.Scatter(x=lx, y=ly, mode="text", text=lt, textposition=lp, textfont=dict(size=12), hoverinfo="skip", showlegend=False))
    fig.update_layout(xaxis=dict(visible=False, range=[-1.9, 1.9]), yaxis=dict(visible=False, range=[-1.25, 1.25], scaleanchor="x"), margin=dict(l=0, r=0, t=10, b=0))
    return fig

def render():
    css("tab05")
    hero("05", "Perempuan bergerak", "Ketika kondisi antarwilayah berbeda, bagaimana penduduk bergerak di antaranya?")
    st.markdown("<p class='lead'>Bab sebelumnya menunjukkan bahwa kondisi perempuan tidak sama di setiap wilayah. "
                "Perbedaan itu tidak hanya terlihat dari pendidikan, pekerjaan, kesehatan, atau kondisi ekonomi. "
                "Penduduk juga bergerak dari satu wilayah ke wilayah lainnya.</p>"
                "<p class='lead'>Dalam data migran resmi Long Form Sensus Penduduk 2020 dari "
                "<a href='https://sensus.bps.go.id/topik/tabular/sp2022/172/0/0' target='_blank'>Badan Pusat Statistik (BPS)</a> "
                "yang dirilis pada tahun 2022, <b>47,68% migran adalah perempuan</b>. "
                "Artinya, perempuan merupakan bagian yang cukup terwakili dari mobilitas penduduk antardaerah.</p>", unsafe_allow_html=True)
    od = load("migrasi_od.csv")
    provs = sorted(set(od.asal) | set(od.tujuan))
    c1, c2 = st.columns(2)
    n = c1.slider("Jumlah arus terbesar", 10, 60, 30)
    s = c2.selectbox("Fokus pada satu provinsi", ["Semua provinsi"] + provs)
    sub = od if s == "Semua provinsi" else od[(od.asal == s) | (od.tujuan == s)]
    fl = sub.nlargest(n, "jumlah")

    st.markdown("#### Lingkaran Arus")
    st.markdown("<p class='lead'>Setiap provinsi tidak hanya menjadi tempat asal, tetapi juga dapat menjadi tujuan perpindahan. "
                "Lebar busur menunjukkan besarnya arus, sedangkan warna mengikuti provinsi asal.</p>", unsafe_allow_html=True)
    st.caption("Lebar busur menunjukkan besarnya arus. Warna mengikuti provinsi asal. Arahkan kursor ke pita untuk melihat angkanya.")
    st.plotly_chart(style_fig(chord(fl), 860), width="stretch")
    sumber("migrasi")
    st.markdown("<p class='lead'>Mobilitas ini memperlihatkan bahwa penduduk tidak berada dalam ruang yang sepenuhnya tetap. "
                "Mereka bergerak di antara wilayah dengan karakteristik yang berbeda.</p>", unsafe_allow_html=True)

    st.markdown("#### Aliran dari provinsi asal ke provinsi tujuan")
    src, dst = sorted(fl.asal.unique()), sorted(fl.tujuan.unique()); nodes = src + [x + " " for x in dst]; ix = {x: i for i, x in enumerate(nodes)}
    ck = {x: PAL[i % len(PAL)] for i, x in enumerate(src)}
    sk = go.Figure(go.Sankey(arrangement="snap", node=dict(label=nodes, color=[ck[x] for x in src] + [PLUM] * len(dst), pad=14, thickness=16),
                             link=dict(source=[ix[x] for x in fl.asal], target=[ix[x + " "] for x in fl.tujuan], value=fl.jumlah,
                                       color=[rgba(ck[x], .45) for x in fl.asal])))
    sk.update_layout(title=f"Migrasi risen {TAHUN_MIGRASI}: asal (kiri) menuju tujuan (kanan)", font=dict(size=13))
    st.plotly_chart(style_fig(sk, max(520, 26 * max(len(src), len(dst)))), width="stretch")
    sumber("migrasi")

    cards = "".join(f"<div class='rec'><b>{a}</b><p>{b}</p></div>" for a, b in REK)
    st.markdown("<div class='closing'><h2>Setara, belum merata.</h2>"
                "<p>Kesenjangan itu masih ada, tapi bentuknya tidak sama. Ada yang mulai sejak usia muda, ada yang terasa di "
                "pekerjaan dan kepemimpinan, ada pula yang baru terlihat saat satu wilayah dibandingkan dengan wilayah lain.</p>"
                "<p>Karena itu, kesetaraan bukan berarti semua orang berdiri di titik yang sama. "
                "<mark class='hl'>Titik awal tidak boleh menentukan seberapa jauh seorang perempuan boleh melangkah.</mark></p>"
                f"<h3>Apa yang bisa dilakukan?</h3><div class='recs'>{cards}</div></div>", unsafe_allow_html=True)
    restart_button(0, "Mau menelusuri lagi dari awal?")
