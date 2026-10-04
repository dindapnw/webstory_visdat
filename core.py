"""Fungsi bersama: palet, CSS loader, komponen UI, navigasi antar-bab."""
import streamlit as st, pandas as pd
from pathlib import Path

ROOT = Path(__file__).parent
PLUM, TEAL, SKY, ORANGE, OFF, CHAR = "#5B3A5E", "#009E73", "#56B4E9", "#E69F00", "#F7F5F2", "#252525"
CLUSTER_COLORS = [TEAL, ORANGE, SKY, PLUM, "#D55E00", "#CC79A7"]
SEQ = ["#D9C2DC", "#B98FBE", "#955F9C", "#74407B", "#4A2A4E"]  # palet sekuensial peta

# Sesuaikan dengan GeoJSON-mu (nama properti kode & nama wilayah)
GEO_PROP, GEO_NAME = "kode_kabkota", "nama"

TAHUN_MIGRASI = 2022  # tahun data migrasi risen; ditampilkan di Tab 05
LABELS = ["01 · Setara?", "02 · Dini", "03 · Kesempatan", "04 · Pola", "05 · Bergerak"]


def css(*names):
    for n in names:
        p = ROOT / "styles" / f"{n}.css"
        st.markdown(f"<style>{p.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


@st.cache_data
def load(name):
    return pd.read_csv(ROOT / "data" / name)


def exists(name):
    return (ROOT / "data" / name).exists()


def hero(num, title, question, cls=""):
    st.markdown(f"<div class='hero {cls}'><span class='num'>Bab {num}</span><h1>{title}</h1>"
                f"<p class='q'>{question}</p></div>", unsafe_allow_html=True)


def quote(text):
    st.markdown(f"<div class='quote'>{text}</div>", unsafe_allow_html=True)


def kpis(items):
    """items: (label, nilai, catatan, persen_opsional). Semua kartu sama tinggi (grid)."""
    h = ""
    for it in items:
        l, v, n, p = (list(it) + [None])[:4]
        bar = f"<div class='bar'><i style='width:{min(float(p), 100)}%'></i></div>" if p is not None else ""
        h += f"<div class='kpi'><span>{l}</span><b>{v}</b>{bar}<small>{n}</small></div>"
    st.markdown(f"<div class='kpi-grid{' one' if len(items) == 1 else ''}'>{h}</div>", unsafe_allow_html=True)


def style_fig(fig, h=440):
    fig.update_layout(height=int(h * .9), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font=dict(family="Plus Jakarta Sans, sans-serif", size=14, color=CHAR),
                      hoverlabel=dict(font_size=14, bgcolor="#fff", bordercolor=PLUM),
                      legend=dict(orientation="h", y=-0.12),
                      margin=dict(l=10, r=10, t=44, b=10), title_font=dict(size=16))
    return fig


def goto(i):
    st.session_state["nav"] = LABELS[i]


def restart_button(i, text):
    """Tombol kembali ke awal: sengaja berbeda gaya dan posisi dari tombol lanjut."""
    with st.container(key="restart"):
        st.button(text, on_click=goto, args=(i,), key=f"restart_{i}", type="secondary")


def next_button(i, text):
    """Tombol penutup bab: pindah ke bab i."""
    st.markdown("<div class='next-wrap'></div>", unsafe_allow_html=True)
    st.button(text, on_click=goto, args=(i,), key=f"next_{i}", type="primary")

from sumber import sumber, IDENTITAS  # noqa
