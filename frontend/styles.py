"""CSS global NidBuyer – sidebar bleu nuit + dashboard blanc."""

MAIN_CSS = """
<style>
/* ── Imports ──────────────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* ── Reset global ─────────────────────────────────────────────────────────── */
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
[data-testid="stAppViewContainer"] { background: #f1f5f9; }
.stApp { background: #f1f5f9; }
[data-testid="stHeader"] { background: transparent !important; }
footer { display: none !important; }

/* ── SIDEBAR BLEU NUIT ───────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: #0b1f3a !important;
    border-right: none !important;
}
[data-testid="stSidebar"] > div:first-child {
    background: #0b1f3a !important;
}
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div { color: #cbd5e1 !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #f8fafc !important; }

/* Inputs sidebar */
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] textarea,
[data-testid="stSidebar"] select {
    background: #152d4a !important;
    color: #f1f5f9 !important;
    border: 1px solid #1e4070 !important;
    border-radius: 8px !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background: #152d4a !important;
    border: 1px solid #1e4070 !important;
    border-radius: 8px !important;
    color: #f1f5f9 !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] svg { fill: #94a3b8 !important; }

/* Bouton principal sidebar */
[data-testid="stSidebar"] .stButton > button {
    background: linear-gradient(135deg, #f97316, #ea580c) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: 0.95em !important;
    padding: 10px 0 !important;
    transition: opacity 0.2s !important;
}
[data-testid="stSidebar"] .stButton > button:hover { opacity: 0.88 !important; }

/* Sliders sidebar */
[data-testid="stSidebar"] [data-testid="stSlider"] { color: #cbd5e1 !important; }

/* ── HEADER PROFIL ────────────────────────────────────────────────────────── */
.prof-header {
    background: white;
    border-radius: 16px;
    padding: 22px 28px;
    margin-bottom: 20px;
    box-shadow: 0 2px 12px rgba(11,31,58,0.08);
    display: flex;
    align-items: center;
    gap: 18px;
    border-left: 5px solid #f97316;
}
.prof-header-icon { font-size: 2.6em; line-height: 1; }
.prof-header-name { font-size: 1.5em; font-weight: 800; color: #0b1f3a; margin: 0; }
.prof-header-desc { color: #64748b; margin: 3px 0 0; font-size: 0.93em; }

/* ── KPI CARDS ────────────────────────────────────────────────────────────── */
.kpi-card {
    background: white;
    border-radius: 14px;
    padding: 18px 20px;
    box-shadow: 0 2px 12px rgba(11,31,58,0.07);
    border-top: 3px solid #e2e8f0;
    text-align: center;
    transition: transform 0.15s;
}
.kpi-card:hover { transform: translateY(-2px); }
.kpi-card.blue   { border-top-color: #3b82f6; }
.kpi-card.orange { border-top-color: #f97316; }
.kpi-card.green  { border-top-color: #22c55e; }
.kpi-card.purple { border-top-color: #8b5cf6; }
.kpi-card.teal   { border-top-color: #14b8a6; }
.kpi-card.rose   { border-top-color: #f43f5e; }
.kpi-icon  { font-size: 1.5em; margin-bottom: 6px; }
.kpi-value { font-size: 1.6em; font-weight: 800; color: #0b1f3a; line-height: 1.1; }
.kpi-label { font-size: 0.75em; color: #94a3b8; font-weight: 600;
             text-transform: uppercase; letter-spacing: 0.5px; margin-top: 4px; }

/* ── NAV MENU SIDEBAR ─────────────────────────────────────────────────────── */
.nav-item {
    display: flex; align-items: center; gap: 10px;
    padding: 10px 14px; border-radius: 10px; cursor: pointer;
    color: #94a3b8; font-size: 0.9em; font-weight: 500;
    margin-bottom: 4px; transition: background 0.15s, color 0.15s;
    text-decoration: none;
}
.nav-item:hover  { background: rgba(255,255,255,0.08); color: #f1f5f9; }
.nav-item.active { background: rgba(249,115,22,0.18); color: #fdba74; font-weight: 700; }
.nav-icon { width: 20px; text-align: center; font-size: 1em; }

/* ── LOGO SIDEBAR ─────────────────────────────────────────────────────────── */
.sidebar-logo {
    display: flex; align-items: center; gap: 12px;
    padding: 8px 4px 4px; margin-bottom: 4px;
}
.sidebar-logo-icon { font-size: 2em; }
.sidebar-logo-title { font-size: 1.3em; font-weight: 800; color: #f8fafc; }
.sidebar-logo-sub { font-size: 0.7em; color: #64748b; font-weight: 400; line-height: 1.3; }

/* ── CARTES BIENS ─────────────────────────────────────────────────────────── */
.bien-card {
    background: white; border-radius: 14px;
    box-shadow: 0 2px 14px rgba(11,31,58,0.07);
    overflow: hidden; margin-bottom: 14px;
    transition: box-shadow 0.2s, transform 0.15s;
}
.bien-card:hover {
    box-shadow: 0 6px 28px rgba(11,31,58,0.12);
    transform: translateY(-2px);
}
.bien-img {
    width: 100%; height: 160px; object-fit: cover;
    background: linear-gradient(135deg, #1e3a5f, #2d5f8a);
    display: flex; align-items: center; justify-content: center;
    font-size: 3em; color: rgba(255,255,255,0.3);
}
.bien-body { padding: 14px 16px; }
.bien-prix { font-size: 1.2em; font-weight: 800; color: #0b1f3a; }
.bien-titre { font-weight: 600; color: #334155; font-size: 0.9em; margin: 4px 0; }
.bien-loc   { color: #64748b; font-size: 0.82em; }
.bien-tags  { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 8px; }
.bien-tag {
    background: #f1f5f9; color: #475569;
    padding: 2px 8px; border-radius: 20px;
    font-size: 0.75em; font-weight: 600;
}
.bien-score { margin-top: 8px; }
.bien-link { margin-top: 8px; }
.bien-link a { color: #f97316; font-size: 0.83em; font-weight: 600; text-decoration: none; }
.bien-link a:hover { text-decoration: underline; }

/* ── BADGES SCORE ─────────────────────────────────────────────────────────── */
.sbadge {
    display: inline-block; padding: 3px 10px;
    border-radius: 20px; font-size: 0.76em; font-weight: 700;
}
.sb-excellent  { background: #d1fae5; color: #065f46; }
.sb-tres-bon   { background: #dcfce7; color: #166534; }
.sb-bon        { background: #fef3c7; color: #92400e; }
.sb-moyen      { background: #ffedd5; color: #9a3412; }
.sb-risque     { background: #fee2e2; color: #991b1b; }
.sb-nd         { background: #f1f5f9; color: #64748b; }

/* ── FICHE DÉCISION ───────────────────────────────────────────────────────── */
.dec-card {
    background: linear-gradient(135deg, #0b1f3a 0%, #1a3f6e 100%);
    border-radius: 16px; padding: 24px; color: white;
}
.dec-card h3 { color: white !important; margin-bottom: 16px; font-size: 1.05em; }
.dec-row {
    background: rgba(255,255,255,0.08); border-radius: 10px;
    padding: 11px 14px; margin-bottom: 8px;
}
.dec-lbl { font-size: 0.72em; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; }
.dec-val { color: #f1f5f9; font-weight: 600; margin-top: 3px; font-size: 0.9em; }

/* ── CHATBOT ──────────────────────────────────────────────────────────────── */
.chat-wrap {
    background: white; border-radius: 14px;
    padding: 16px 18px 10px;
    box-shadow: 0 2px 14px rgba(11,31,58,0.07);
    max-height: 360px; overflow-y: auto; margin-bottom: 10px;
}
.chat-user {
    background: #0b1f3a; color: white;
    border-radius: 16px 16px 4px 16px;
    padding: 9px 14px; margin: 6px 0 6px auto;
    max-width: 80%; display: table; margin-left: auto;
    font-size: 0.88em; line-height: 1.45;
}
.chat-bot {
    background: #f1f5f9; color: #1e293b;
    border-radius: 16px 16px 16px 4px;
    padding: 9px 14px; margin: 6px auto 6px 0;
    max-width: 80%; display: table;
    font-size: 0.88em; line-height: 1.45;
}

/* ── SECTION TITLES ───────────────────────────────────────────────────────── */
.sec-title {
    color: #0b1f3a; font-weight: 800; font-size: 1.05em;
    margin-bottom: 14px; padding-bottom: 8px;
    border-bottom: 2px solid #e2e8f0;
}

/* ── STATE EMPTY ──────────────────────────────────────────────────────────── */
.empty-state {
    background: white; border-radius: 14px; padding: 40px;
    text-align: center; color: #94a3b8;
    box-shadow: 0 2px 12px rgba(11,31,58,0.06);
}
.empty-icon { font-size: 3em; margin-bottom: 12px; }
.empty-text { font-size: 1em; color: #64748b; }

/* ── STREAMLIT OVERRIDES ──────────────────────────────────────────────────── */
div[data-testid="stMetric"] {
    background: white; border-radius: 12px;
    padding: 14px 16px;
    box-shadow: 0 2px 10px rgba(11,31,58,0.06);
}
.stTabs [data-baseweb="tab-list"] {
    background: white; border-radius: 12px 12px 0 0;
    padding: 6px 10px 0; gap: 4px;
    box-shadow: 0 2px 12px rgba(11,31,58,0.06);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px 8px 0 0 !important;
    font-weight: 600 !important; font-size: 0.88em !important;
    color: #64748b !important;
}
.stTabs [aria-selected="true"] {
    background: #0b1f3a !important; color: white !important;
}
.stTabs [data-testid="stTabsContent"] {
    background: white; border-radius: 0 0 12px 12px;
    box-shadow: 0 2px 12px rgba(11,31,58,0.06);
    padding: 20px;
}
</style>
"""
