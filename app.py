import importlib, streamlit as st, streamlit.components.v1 as components
from core import LABELS, css, IDENTITAS

st.set_page_config(page_title="Setara, Belum Merata", page_icon="◐", layout="wide")
css("base")
if "nav" not in st.session_state:
    st.session_state["nav"] = LABELS[0]

st.markdown("<div class='mast'>Setara, Belum Merata</div>", unsafe_allow_html=True)
st.radio("Bab", LABELS, key="nav", horizontal=True, label_visibility="collapsed")
idx = LABELS.index(st.session_state["nav"])
st.markdown(f"<div class='progress'><div style='width:{(idx+1)/len(LABELS)*100}%'></div></div>", unsafe_allow_html=True)

mods = ["tab01_setara", "tab02_dini", "tab03_kesempatan", "tab04_pola", "tab05_bergerak"]
importlib.import_module(f"tabs.{mods[idx]}").render()

st.markdown(f"<div class='foot'>{IDENTITAS}</div>", unsafe_allow_html=True)
components.html(f"<!--{idx}--><script>const m=window.parent.document.querySelector('[data-testid=stMain]');"
                "if(m)m.scrollTo(0,0);</script>", height=0)
