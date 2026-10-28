"""Luxury burgundy theme for the EstateFrame Streamlit application."""
from __future__ import annotations

import streamlit as st

CSS = r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:wght@500;600;700&display=swap');
:root {
  --bg:#2C1512;
  --nav:#24120F;
  --surface:#37211E;
  --raised:#442925;
  --accent:#8B2D3A;
  --accent-hi:#A74351;
  --accent-soft:#4A242A;
  --accent-text:#E8B8BE;
  --text:#FFFFFF;
  --muted:#C5B5AF;
  --line:#563A35;
  --success:#8EC6A1;
  --danger:#E6A3A3;
  --input:#2C1916;
}

html, body, [class*="css"] {
  font-family:Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"], section.main {
  background:var(--bg)!important; color:var(--text)!important;
}
[data-testid="stSidebar"] { display:none!important; }
/* Remove Streamlit's reserved toolbar gap and align the app to the top of the viewport. */
[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"], #MainMenu, footer {
  display:none!important; visibility:hidden!important; height:0!important; min-height:0!important;
}
[data-testid="stAppViewContainer"] > .main,
[data-testid="stMain"], section.main {
  margin-top:0!important; padding-top:0!important; top:0!important;
}
[data-testid="stMainBlockContainer"], .stMainBlockContainer,
.stAppViewBlockContainer, section.main > div.block-container, .main .block-container {
  width:100%!important; max-width:1480px!important; box-sizing:border-box!important;
  margin:0 auto!important; padding:.65rem clamp(1rem,2.5vw,2.25rem) 2.5rem!important;
  position:relative!important; top:0!important;
}
[data-testid="stVerticalBlock"] { gap:.68rem; }
[data-testid="stMarkdownContainer"] { color:var(--text); }
[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3 { color:var(--text)!important; letter-spacing:-.025em; }
h1 { font-family:'Playfair Display',Georgia,serif!important; font-size:2.05rem!important; line-height:1.16!important; font-weight:600!important; margin:.05rem 0 .42rem!important; }
h2 { font-size:1.22rem!important; line-height:1.3!important; font-weight:600!important; }
h3 { font-size:1rem!important; font-weight:600!important; }
p, li { color:var(--muted); line-height:1.55; }
small, .stCaption, [data-testid="stCaptionContainer"] { color:var(--muted)!important; }
hr { border-color:var(--line)!important; margin:.85rem 0!important; }
[data-testid="stImage"] img { border-radius:8px; object-fit:cover; }

/* Top navigation */
.st-key-top_navigation {
  width:100%!important; box-sizing:border-box!important; background:var(--nav)!important;
  border:1px solid var(--line)!important; border-radius:10px!important;
  padding:.32rem .68rem!important; margin:0 0 1.05rem!important; min-height:60px;
}
.st-key-top_navigation [data-testid="stHorizontalBlock"] { align-items:center!important; gap:.36rem!important; }
.st-key-top_navigation [data-testid="column"] { min-width:0!important; justify-content:center!important; }
.brand-lockup { display:flex; align-items:center; gap:10px; min-height:44px; min-width:0; }
.brand-mark {
  width:35px; height:35px; flex:0 0 35px; display:flex; align-items:center; justify-content:center;
  background:var(--accent); color:#FFFFFF!important; border:1px solid #B05B66; border-radius:8px;
  font-size:.8rem; font-weight:700; letter-spacing:-.04em;
}
.brand-name { color:var(--text)!important; font-family:'Playfair Display',Georgia,serif; font-weight:600; font-size:1.2rem; letter-spacing:-.025em; line-height:1.1; white-space:nowrap; }
.brand-sub { color:#C6AFA9!important; font-size:.55rem; letter-spacing:.09em; margin-top:4px; white-space:nowrap; }
.st-key-top_navigation [class*="st-key-top_nav_"] .stButton > button {
  background:transparent!important; border:1px solid transparent!important; color:#D9CAC5!important;
  -webkit-text-fill-color:#D9CAC5!important; border-radius:6px!important; min-height:2.25rem!important;
  padding:.32rem .42rem!important; font-size:.76rem!important; font-weight:500!important;
  box-shadow:none!important; white-space:nowrap!important;
}
.st-key-top_navigation [class*="st-key-top_nav_"] .stButton > button:hover {
  background:#3E2420!important; color:#FFFFFF!important; -webkit-text-fill-color:#FFFFFF!important; border-color:var(--line)!important;
}
.st-key-top_nav_home_active .stButton > button,
.st-key-top_nav_create_video_active .stButton > button,
.st-key-top_nav_my_videos_active .stButton > button,
.st-key-top_nav_templates_active .stButton > button {
  color:#FFFFFF!important; -webkit-text-fill-color:#FFFFFF!important;
  background:var(--accent-soft)!important; border:1px solid #71303A!important;
  box-shadow:inset 0 -2px 0 var(--accent)!important;
}

/* Page headers and home hero */
.page-eyebrow, .section-label {
  color:#DDA4AC!important; font-size:.64rem; font-weight:700; letter-spacing:.14em;
  margin:.55rem 0 .42rem; text-transform:uppercase;
}
.page-subtitle { color:var(--muted)!important; font-size:.84rem; margin-top:0; margin-bottom:.9rem; }
.hero-title {
  color:var(--text)!important; font-family:'Playfair Display',Georgia,serif; font-weight:600;
  letter-spacing:-.045em; font-size:clamp(2.15rem,3.35vw,3.25rem); line-height:1.08;
  margin:.5rem 0 .8rem;
}
.hero-title span { color:#D98D98!important; }
.hero-desc { color:#D3C4BF!important; font-size:.9rem; line-height:1.65; max-width:440px; margin:0 0 1.1rem; }
.hero-chip, .pill {
  display:inline-flex; align-items:center; gap:5px; background:var(--accent-soft)!important;
  color:#F1DDE0!important; border:1px solid #75404A!important; padding:4px 8px;
  border-radius:5px; font-size:.64rem; font-weight:600;
}
.hero-image-caption { display:flex; align-items:center; justify-content:space-between; gap:.75rem; padding:.3rem .1rem 0; }
.hero-image-caption strong { color:var(--text)!important; font-size:.82rem; font-weight:600; }
.hero-image-caption span { color:var(--muted)!important; font-size:.72rem; }
.section-head { display:flex; align-items:flex-end; justify-content:space-between; margin:.55rem 0 .3rem; }
.feature-card { min-height:0; padding:.72rem .5rem .75rem; border:0; border-top:1px solid var(--line); border-radius:0; background:transparent; }
.feature-icon { color:#DDA4AC!important; font-size:1.05rem; margin-bottom:.3rem; }
.feature-title { color:var(--text)!important; font-size:.79rem; font-weight:600; margin-bottom:.15rem; }
.feature-desc { color:var(--muted)!important; font-size:.69rem; line-height:1.45; }
.sample-name { color:var(--text)!important; font-size:.79rem; font-weight:600; margin:.35rem 0 .1rem; }
.sample-location { color:var(--muted)!important; font-size:.7rem; }

/* Cards and panels */
[data-testid="stVerticalBlockBorderWrapper"] {
  background:var(--surface)!important; border:1px solid var(--line)!important;
  border-radius:10px!important; box-shadow:none!important;
}
.card-title { color:var(--text)!important; font-size:.95rem; font-weight:600; letter-spacing:-.012em; margin:0 0 .2rem; }
.card-subtitle { color:var(--muted)!important; font-size:.75rem; line-height:1.5; margin:0 0 .78rem; }
.muted-note { color:var(--muted)!important; font-size:.75rem; line-height:1.5; }
.photo-label { color:var(--text)!important; font-size:.76rem; font-weight:500; margin:.35rem 0; overflow-wrap:anywhere; }
.style-title { color:var(--text)!important; font-size:.89rem; font-weight:600; margin:.3rem 0 .15rem; }
.style-desc { color:var(--muted)!important; font-size:.7rem; line-height:1.45; min-height:2.2rem; }

/* Inputs */
[data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] label { color:#E6D8D3!important; font-size:.74rem!important; font-weight:500!important; }
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stNumberInput"] input,
[data-testid="stDateInput"] input,
[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
[data-testid="stMultiSelect"] div[data-baseweb="select"] > div {
  background:var(--input)!important; color:var(--text)!important; -webkit-text-fill-color:var(--text)!important;
  border:1px solid #64443E!important; border-radius:7px!important; min-height:2.42rem; box-shadow:none!important;
}
[data-testid="stTextInput"] input::placeholder, [data-testid="stTextArea"] textarea::placeholder { color:#B29F99!important; -webkit-text-fill-color:#B29F99!important; }
[data-testid="stTextArea"] textarea { min-height:5rem; }
[data-testid="stTextInput"] input:focus, [data-testid="stTextArea"] textarea:focus,
[data-testid="stSelectbox"] div[data-baseweb="select"] > div:focus-within,
[data-testid="stMultiSelect"] div[data-baseweb="select"] > div:focus-within,
[data-testid="stNumberInput"] input:focus { border-color:#B65D69!important; box-shadow:0 0 0 1px #B65D69!important; }
[data-baseweb="popover"] [role="listbox"], [data-baseweb="menu"] { background:#37211E!important; border:1px solid var(--line)!important; }
[data-baseweb="popover"] [role="option"], [data-baseweb="popover"] [role="option"] * { color:var(--text)!important; }
[data-baseweb="tag"] { background:var(--accent-soft)!important; border-color:#79434D!important; color:#FFFFFF!important; }
[data-testid="stFileUploaderDropzone"] { border:1px dashed #89545B!important; background:#321B18!important; border-radius:9px!important; padding:.9rem!important; }
[data-testid="stFileUploaderDropzone"] small, [data-testid="stFileUploaderDropzone"] span { color:var(--muted)!important; }
[data-testid="stFileUploaderDropzone"] button { background:#49252A!important; border:1px solid #89505A!important; border-radius:6px!important; color:#FFFFFF!important; -webkit-text-fill-color:#FFFFFF!important; }
[data-testid="stFileUploaderDropzone"] button * { color:#FFFFFF!important; -webkit-text-fill-color:#FFFFFF!important; }
[data-testid="stRadio"] [role="radiogroup"] { gap:.35rem; }
[data-testid="stRadio"] label, [data-testid="stCheckbox"] label, [data-testid="stRadio"] label p, [data-testid="stCheckbox"] label p { color:var(--text)!important; }
[data-testid="stSlider"] [role="slider"] { background:var(--accent)!important; border-color:#FFFFFF!important; }
[data-testid="stExpander"] { border:1px solid var(--line)!important; border-radius:8px!important; background:var(--surface)!important; }
[data-testid="stExpander"] summary { font-weight:500!important; color:var(--text)!important; }

/* High-contrast buttons: force foreground color onto nested Streamlit text nodes too. */
.stButton > button, .stDownloadButton > button, [data-testid^="stBaseButton-"] {
  min-height:2.42rem!important; border-radius:7px!important; border:1px solid #63423C!important;
  background:#432824!important; color:#FFFFFF!important; -webkit-text-fill-color:#FFFFFF!important;
  font-weight:600!important; font-size:.78rem!important; opacity:1!important;
  text-shadow:none!important; box-shadow:none!important; transition:background .14s ease,border-color .14s ease;
}
.stButton > button *, .stDownloadButton > button *, [data-testid^="stBaseButton-"] * {
  color:inherit!important; -webkit-text-fill-color:currentColor!important; opacity:1!important;
}
.stButton > button:hover, .stDownloadButton > button:hover, [data-testid^="stBaseButton-"]:hover {
  border-color:#A64D58!important; background:#4E2A2B!important; color:#FFFFFF!important; -webkit-text-fill-color:#FFFFFF!important;
}
.stButton > button[kind="primary"], .stDownloadButton > button[kind="primary"],
button[data-testid="stBaseButton-primary"], [data-testid="stBaseButton-primary"] {
  background:var(--accent)!important; border-color:var(--accent)!important;
  color:#FFFFFF!important; -webkit-text-fill-color:#FFFFFF!important; font-weight:700!important;
}
.stButton > button[kind="primary"] *, .stDownloadButton > button[kind="primary"] *,
button[data-testid="stBaseButton-primary"] *, [data-testid="stBaseButton-primary"] * {
  color:#FFFFFF!important; -webkit-text-fill-color:#FFFFFF!important;
}
.stButton > button[kind="primary"]:hover, .stDownloadButton > button[kind="primary"]:hover,
button[data-testid="stBaseButton-primary"]:hover, [data-testid="stBaseButton-primary"]:hover {
  background:var(--accent-hi)!important; border-color:var(--accent-hi)!important;
  color:#FFFFFF!important; -webkit-text-fill-color:#FFFFFF!important;
}
.stButton > button:disabled, .stDownloadButton > button:disabled, [data-testid^="stBaseButton-"]:disabled {
  background:#4B3330!important; border-color:#624440!important; color:#D1BEB9!important;
  -webkit-text-fill-color:#D1BEB9!important; opacity:1!important; cursor:not-allowed!important;
}
.stButton > button:disabled *, .stDownloadButton > button:disabled *, [data-testid^="stBaseButton-"]:disabled * {
  color:#D1BEB9!important; -webkit-text-fill-color:#D1BEB9!important;
}

/* Workflow stepper */
.stepper { display:flex; align-items:center; gap:0; padding:.72rem .9rem; background:var(--surface); border:1px solid var(--line); border-radius:9px; margin:.2rem 0 .95rem; }
.step-item { display:flex; align-items:center; gap:.48rem; flex:1; min-width:0; position:relative; }
.step-node { width:26px; height:26px; flex:0 0 26px; display:flex; align-items:center; justify-content:center; border:1px solid #75524A; background:#2C1916; color:#C6B5AE; border-radius:50%; font-size:.7rem; font-weight:600; }
.step-item.active .step-node, .step-item.done .step-node { background:var(--accent); border-color:#B5636D; color:#FFFFFF!important; }
.step-name { color:var(--muted)!important; font-size:.7rem; font-weight:500; white-space:nowrap; }
.step-item.active .step-name { color:#F3CDD2!important; }
.step-item.done .step-name { color:#E7D8D3!important; }
.step-line { height:1px; background:#65453F; flex:.35; margin:0 .6rem; }
.step-line.done { background:#A54D58; }

/* Cover preview */
.poster-frame { position:relative; width:100%; overflow:hidden; background-size:cover; background-position:center; border-radius:8px; color:#FFFFFF; }
.poster-overlay { position:absolute; inset:0; display:flex; flex-direction:column; justify-content:space-between; padding:7%; background:linear-gradient(180deg,rgba(24,9,10,.42),transparent 25%,rgba(24,9,10,.84)); }
.poster-brand { color:#FFFFFF!important; font-size:.62rem; letter-spacing:.13em; font-weight:600; }
.poster-title { color:#FFFFFF!important; font-family:'Playfair Display',Georgia,serif; font-size:clamp(1rem,2.1vw,1.85rem); font-weight:600; line-height:1.1; overflow-wrap:anywhere; }
.poster-sub { color:#F0DFDE!important; font-size:.7rem; margin-top:.4rem; }
.poster-price { display:inline-block; width:max-content; color:#FFFFFF!important; border:1px solid rgba(205,126,137,.7); background:rgba(44,21,18,.72); padding:4px 8px; border-radius:4px; font-size:.72rem; margin-top:.55rem; }
.poster-footer { color:#E7D3CF!important; font-size:.56rem; letter-spacing:.1em; }

/* Progress, result and notices */
[data-testid="stProgressBar"] > div { background:#4B302C!important; }
[data-testid="stProgressBar"] > div > div { background:var(--accent)!important; }
[data-testid="stMetric"] { border:1px solid var(--line); border-radius:7px; padding:.5rem .6rem; background:#2D1916!important; }
[data-testid="stMetricLabel"] { font-size:.65rem!important; color:var(--muted)!important; }
[data-testid="stMetricValue"] { font-weight:600!important; font-size:1.02rem!important; color:var(--text)!important; }
.result-success { display:flex; align-items:center; gap:.75rem; padding:.65rem 0 .9rem; }
.result-check { display:flex; align-items:center; justify-content:center; border-radius:50%; width:34px; height:34px; background:#23392D; color:var(--success)!important; font-size:1.05rem; border:1px solid #3B684B; }
.result-title { color:var(--text)!important; font-size:1.13rem; font-weight:600; }
.result-sub { color:var(--muted)!important; font-size:.75rem; margin-top:.1rem; }
.status-row { display:flex; align-items:center; gap:.55rem; padding:.32rem 0; color:#E4D7D2!important; font-size:.8rem; }
.status-icon { width:20px; height:20px; display:inline-flex; align-items:center; justify-content:center; border:1px solid #6B4B45; border-radius:50%; color:#E4B3B9!important; font-size:.7rem; flex-shrink:0; }
.status-icon.complete { background:#22372B; border-color:#3D644B; color:var(--success)!important; }
.stAlert { background:#422623!important; border:1px solid #72454A!important; color:var(--text)!important; border-radius:8px!important; }
[data-testid="stAlert"] p, [data-testid="stAlert"] span { color:var(--text)!important; }
[data-testid="stAlert"] svg { fill:currentColor!important; }

@media (max-width: 900px) {
  [data-testid="stMainBlockContainer"], .stMainBlockContainer, .stAppViewBlockContainer, section.main > div.block-container, .main .block-container { padding:.5rem 1rem 2rem!important; }
  .st-key-top_navigation { padding:.35rem .45rem!important; min-height:54px; margin-bottom:.85rem!important; }
  .brand-sub { display:none; }
  .brand-mark { width:29px; height:29px; flex-basis:29px; }
  .brand-name { font-size:1rem; }
  .st-key-top_navigation [class*="st-key-top_nav_"] .stButton > button { font-size:.69rem!important; padding:.28rem .22rem!important; }
  .stepper { padding:.6rem .45rem; }
  .step-item { gap:.3rem; }
  .step-node { width:22px; height:22px; flex-basis:22px; font-size:.65rem; }
  .step-name { font-size:.61rem; }
  .step-line { margin:0 .25rem; }
}
@media (max-width: 600px) {
  [data-testid="stMainBlockContainer"], .stMainBlockContainer, .stAppViewBlockContainer, section.main > div.block-container, .main .block-container { padding:.4rem .65rem 1.4rem!important; }
  .hero-title { font-size:2.05rem; }
  .page-subtitle { font-size:.77rem; }
  .step-name { white-space:normal; }
  .brand-name { font-size:.9rem; }
}
</style>
"""


def apply_styles() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
