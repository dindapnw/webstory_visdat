import textwrap, streamlit as st, numpy as np, pandas as pd, plotly.express as px, plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, davies_bouldin_score
from sklearn.preprocessing import StandardScaler
from core import *

# kolom -> (label, tahun)
V = {"tpak": ("TPAK perempuan", 2024), "sumbangan_pendapatan": ("Sumbangan pendapatan", 2024),
     "tenaga_profesional": ("Tenaga profesional", 2024), "parlemen": ("Keterwakilan parlemen", 2024),
     "rls": ("Rata-rata lama sekolah", 2024), "ahh": ("Angka harapan hidup", 2024),
     "pengeluaran": ("Pengeluaran per kapita", 2024), "pdrb_kapita": ("PDRB per kapita", 2024),
     "gini": ("Gini ratio", 2024)}
SH = {k: v[0] for k, v in V.items()}
K_OVERRIDE = None  # isi angka (mis. 3) hanya jika ingin mengabaikan pilihan otomatis

@st.cache_data
def pilih_k(X):
    """Jumlah kelompok dipilih otomatis: skor silhouette tertinggi, dengan syarat tiap kelompok minimal 2 provinsi."""
    rows = []
    for k in range(2, 7):
        lab = KMeans(k, n_init=10, random_state=1).fit_predict(X)
        rows.append((k, silhouette_score(X, lab), davies_bouldin_score(X, lab), int(np.bincount(lab).min())))
    t = pd.DataFrame(rows, columns=["Jumlah kelompok", "Silhouette (makin tinggi makin baik)", "Davies-Bouldin (makin rendah makin baik)", "Anggota terkecil"])
    ok = t[t["Anggota terkecil"] >= 2]
    return t, int(ok.loc[ok.iloc[:, 1].idxmax(), "Jumlah kelompok"])

def render():
    css("tab04")
    hero("04", "Titik mulai yang berbeda", "Jika semua aspek dilihat bersamaan, pola apa yang muncul?")
    st.markdown("<p class='lead'>Sembilan indikator kita rangkum jadi dua dimensi (skor ringkasan). Provinsi yang letaknya berdekatan "
                "punya kondisi yang mirip. Tujuannya melihat pola, bukan mencari provinsi terbaik.</p>", unsafe_allow_html=True)
    st.caption("Semua indikator tahun 2024 (Gini: September). PDRB per kapita diubah ke skala log agar provinsi bernilai ekstrem tidak mendominasi.")
    df = load("provinsi.csv").copy(); cols = list(V)
    X = StandardScaler().fit_transform(df[cols].assign(pdrb_kapita=np.log(df.pdrb_kapita)))
    pca = PCA(2).fit(X); P = pca.transform(X); df["PC1"], df["PC2"] = P[:, 0], P[:, 1]
    ld = pd.DataFrame(pca.components_.T, index=cols)
    tabk, best = pilih_k(X); k = K_OVERRIDE or best
    km = KMeans(k, n_init=10, random_state=1).fit(X)
    df["Kelompok"] = [f"K{i+1}" for i in km.labels_]
    df["jarak"] = np.linalg.norm(X - km.cluster_centers_[km.labels_], axis=1)
    cmap = {f"K{i+1}": CLUSTER_COLORS[i] for i in range(k)}; Z = pd.DataFrame(X, columns=cols)

    sk = tabk.set_index("Jumlah kelompok").iloc[:, 0]
    st.markdown("<div class='callout'><b>Cara membaca kelompok.</b> Kelompok adalah golongan provinsi dengan kondisi yang paling mirip. "
                f"Jumlah kelompok ditentukan secara statistik: dari 2 sampai 6 kelompok yang dicoba, pemisahan paling jelas diperoleh pada <b>{k} kelompok</b> "
                f"(skor silhouette {sk[k]:.2f}). Pengelompokan memakai metode K-Means, lalu ciri tiap kelompok dibaca pada bagian di bawah.</div>", unsafe_allow_html=True)
    with st.expander("Lihat dasar pemilihan jumlah kelompok"):
        st.dataframe(tabk.round(3), hide_index=True, width="stretch")
        st.caption("Silhouette mengukur seberapa jelas provinsi terpisah antarkelompok. Syarat tambahan: tiap kelompok minimal berisi 2 provinsi, "
                   "agar satu provinsi yang menyimpang tidak dihitung sebagai kelompok sendiri (provinsi seperti itu dibahas sebagai pencilan).")

    st.markdown("#### 1 · Provinsi yang mirip akan berdekatan")
    fig = px.scatter(df, x="PC1", y="PC2", color="Kelompok", color_discrete_map=cmap, custom_data=["provinsi"],
                     hover_name="provinsi", category_orders={"Kelompok": sorted(cmap)})
    fig.update_traces(marker=dict(size=14, line=dict(width=1, color="#fff")),
                      selected=dict(marker=dict(size=22, opacity=1)), unselected=dict(marker=dict(opacity=.35)))
    fig.update_layout(xaxis_title=f"Dimensi 1 ({pca.explained_variance_ratio_[0]:.0%})", yaxis_title=f"Dimensi 2 ({pca.explained_variance_ratio_[1]:.0%})")
    ev = st.plotly_chart(style_fig(fig, 480), width="stretch", on_select="rerun", selection_mode=("points", "box", "lasso"), key="pca04")
    dim = lambda j: ", ".join(f"{SH[c]} ({'+' if ld.loc[c, j] > 0 else '−'})" for c in ld[j].abs().nlargest(3).index)
    st.caption(f"Dimensi 1 paling dipengaruhi: {dim(0)}. Dimensi 2: {dim(1)}. Tanda (+) berarti makin besar nilainya, provinsi makin ke kanan/atas; (−) sebaliknya.")
    sel = [p["customdata"][0] for p in (ev.selection.points if ev and ev.selection else [])]
    pilih = st.multiselect("Pilih provinsi untuk disorot di grafik lain", list(df.provinsi))
    sel = pilih or sel
    sumber("pola")

    st.markdown("#### 2 · Seperti apa tiap kelompok?")
    cz = Z.assign(K=df.Kelompok.values).groupby("K")[cols].mean(); cards = ""
    for kn in sorted(cmap):
        mem = list(df.provinsi[df.Kelompok == kn]); r = cz.loc[kn]
        hi = [SH[c] for c in r.nlargest(3).index if r[c] > .4]; lo = [SH[c] for c in r.nsmallest(3).index if r[c] < -.4]
        txt = (f"<b>Lebih tinggi</b> dari rata-rata 38 provinsi: {', '.join(hi)}. " if hi else "") + (f"<b>Lebih rendah</b>: {', '.join(lo)}." if lo else "")
        cards += (f"<div class='kcard' style='border-top-color:{cmap[kn]}'><h5>{kn} · {len(mem)} provinsi</h5><p>{txt or 'Mendekati rata-rata hampir semua indikator.'}</p>"
                  f"<small>{', '.join(mem[:6])}{' dan lainnya' if len(mem) > 6 else ''}</small></div>")
    st.markdown(f"<div class='kgrid'>{cards}</div>", unsafe_allow_html=True)
    with st.expander("Lihat angka rata-rata tiap kelompok"):
        st.dataframe(df.groupby("Kelompok")[cols].mean().round(1).rename(columns=SH).T, width="stretch")
    st.caption("Catatan: 'lebih tinggi' hanya menunjukkan angka, bukan baik atau buruk. Pada Gini ratio, angka lebih tinggi berarti pengeluaran lebih timpang.")

    st.markdown("#### 3 · Apakah dua indikator bergerak bersama?")
    pick = st.multiselect("Pilih indikator (maksimal 4)", cols, default=cols[:4], format_func=SH.get, max_selections=4)
    st.caption("Setiap kotak membandingkan dua indikator; satu titik mewakili satu provinsi. Nama indikator tertera pada kotak abu-abu di diagonal; kotak itu menjadi nama baris dan kolomnya.")
    if len(pick) >= 2:
        n = len(pick); hs = vs = .045; w = (1 - (n - 1) * hs) / n; h = (1 - (n - 1) * vs) / n
        f3 = make_subplots(rows=n, cols=n, horizontal_spacing=hs, vertical_spacing=vs)
        rng = {c: [df[c].min() - .06 * (df[c].max() - df[c].min()), df[c].max() + .06 * (df[c].max() - df[c].min())] for c in pick}
        for i, ci in enumerate(pick):
            for j, cj in enumerate(pick):
                if i == j:
                    f3.update_xaxes(visible=False, row=i + 1, col=j + 1); f3.update_yaxes(visible=False, row=i + 1, col=j + 1); continue
                for kn in sorted(cmap):
                    m = df.Kelompok == kn; on = df.provinsi[m].isin(sel)
                    f3.add_trace(go.Scatter(x=df.loc[m, cj], y=df.loc[m, ci], mode="markers", name=kn, legendgroup=kn, showlegend=(i == 0 and j == 1),
                                            marker=dict(color=cmap[kn], size=np.where(on, 12, 7), symbol=np.where(on, "diamond", "circle"), line=dict(width=.5, color="#fff")),
                                            text=df.provinsi[m], hovertemplate="<b>%{text}</b><br>" + SH[cj] + ": %{x:.1f}<br>" + SH[ci] + ": %{y:.1f}<extra></extra>"),
                                 row=i + 1, col=j + 1)
                f3.update_xaxes(range=rng[cj], showticklabels=(i == n - 1), showgrid=True, gridcolor="#ece6ee", tickfont=dict(size=10), row=i + 1, col=j + 1)
                f3.update_yaxes(range=rng[ci], showticklabels=(j == 0), showgrid=True, gridcolor="#ece6ee", tickfont=dict(size=10), row=i + 1, col=j + 1)
        for j, c in enumerate(pick):  # nama indikator di kotak diagonal (posisi dihitung dari susunan kotak)
            x0, y1 = j * (w + hs), 1 - j * (h + vs)
            f3.add_shape(type="rect", xref="paper", yref="paper", x0=x0, x1=x0 + w, y0=y1 - h, y1=y1, fillcolor="#EFE9E2", line_width=0, layer="below")
            f3.add_annotation(x=x0 + w / 2, y=y1 - h / 2, xref="paper", yref="paper", showarrow=False, align="center",
                              text="<b>" + "<br>".join(textwrap.wrap(SH[c], 14)) + "</b>", font=dict(size=15, color=CHAR))
        st.plotly_chart(style_fig(f3, 760).update_layout(margin=dict(l=40, r=10, t=20, b=40)), width="stretch")
        sumber("pola")
    else:
        st.info("Pilih minimal 2 indikator untuk menampilkan perbandingan.")

    st.markdown("#### 4 · Bandingkan provinsi pilihan")
    N = (df[cols] - df[cols].min()) / (df[cols].max() - df[cols].min()); xs = [SH[c] for c in cols]
    f5 = go.Figure()
    for kn in sorted(cmap):
        f5.add_trace(go.Scatter(x=xs, y=N[df.Kelompok == kn].mean().values, mode="lines", name=f"Rata-rata {kn}",
                                line=dict(color=cmap[kn], width=2, dash="dot"), opacity=.8))
    for p in sel:
        i = df.index[df.provinsi == p][0]
        f5.add_trace(go.Scatter(x=xs, y=N.loc[i].values, mode="lines+markers", name=p, line=dict(color=cmap[df.Kelompok[i]], width=4), marker=dict(size=8)))
    f5.update_layout(yaxis=dict(title="Rendah → tinggi", showticklabels=False), xaxis=dict(tickangle=-30))
    st.plotly_chart(style_fig(f5, 480).update_layout(legend=dict(orientation="v", x=1.02, y=1, xanchor="left"), margin=dict(l=10, r=10, t=44, b=10)), width="stretch")
    if not sel:
        st.caption("Pilih provinsi di grafik 1 atau lewat kotak pilihan di atas, garisnya akan muncul di sini. Garis putus-putus adalah rata-rata kelompok.")
    sumber("pola")

    st.markdown("#### 5 · Provinsi yang paling berbeda dari kelompoknya")
    items = ""
    for i, r in df.nlargest(3, "jarak").iterrows():
        dev = pd.Series(X[i] - km.cluster_centers_[km.labels_[i]], index=cols)
        parts = [f"{SH[c]} {'jauh di atas' if dev[c] > 0 else 'jauh di bawah'} rata-rata kelompoknya ({r[c]:,.1f} vs {df.loc[df.Kelompok == r.Kelompok, c].mean():,.1f})"
                 for c in dev.abs().nlargest(2).index]
        items += f"<li><b>{r.provinsi}</b> ({r.Kelompok}): {'; '.join(parts)}.</li>"
    st.markdown(f"<ul class='outl'>{items}</ul><p class='note'>Beberapa provinsi terlihat cukup berbeda dari provinsi lain dalam kelompoknya. "
                "Perbedaan ini tidak selalu berarti lebih baik atau lebih buruk, tetapi menunjukkan bahwa karakteristik suatu wilayah tidak sepenuhnya mengikuti pola kelompoknya.</p>", unsafe_allow_html=True)
    quote("Setiap wilayah punya persoalan yang berbeda, jadi cara mengatasinya pun tidak bisa sama.")
    next_button(4, "Lanjut: perempuan bergerak")
