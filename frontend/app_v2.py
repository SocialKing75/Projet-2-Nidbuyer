"""
NidBuyer — Dashboard SaaS Immobilier · Streamlit v3.0
Lancer : streamlit run frontend/app.py
"""
from __future__ import annotations

import os
import sys

import requests
import streamlit as st

# ── sys.path : racine projet + dossier frontend ──────────────────────────────
_FRONTEND = os.path.dirname(os.path.abspath(__file__))
_ROOT     = os.path.dirname(_FRONTEND)
for _p in (_ROOT, _FRONTEND):
    if _p not in sys.path:
        sys.path.insert(0, _p)

API_URL = (os.getenv("API_URL") or os.getenv("NIDBUYER_API_URL") or "http://localhost:8000").rstrip("/")

# ── Imports locaux (depuis frontend/) ────────────────────────────────────────
from styles import MAIN_CSS                          # noqa: E402
from components import (                             # noqa: E402
    PROFILS_CFG,
    mock_biens,
    render_biens,
    render_chatbot,
    render_charts,
    render_fiche_decision,
    render_header,
    render_kpis,
    render_photos_analysis,
    render_scoring,
)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG  — PREMIER appel Streamlit obligatoire
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="NidBuyer · IA Immobilière",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(MAIN_CSS, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
_DEFAULTS = {
    "profil_key":    "rp",
    "resultats":     [],
    "analyse_done":  False,
    "photo_analysis": {},
    "profil_payload": {},
    "chat_msgs":     [],
    "view":          "dashboard",   # dashboard | biens | analyse | chatbot
}
for _k, _v in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v


# ══════════════════════════════════════════════════════════════════════════════
# API / DONNÉES
# ══════════════════════════════════════════════════════════════════════════════

def _backend_ok() -> bool:
    try:
        return requests.get(f"{API_URL}/admin/status", timeout=5).status_code == 200
    except Exception:
        return False


def _adapt(b: dict) -> dict:
    """Résultat de POST /rechercher → format bien attendu par les composants."""
    return {
        "type":        b.get("type") or "",
        "prix":        b.get("prix") or 0,
        "surface":     b.get("surface") or 0,
        "quartier":    b.get("quartier") or "",
        "ville":       b.get("ville") or "",
        "nb_pieces":   b.get("pieces") or 0,
        "dpe":         b.get("dpe") or "",
        "description": b.get("description") or "",
        "url_source":  b.get("url") or "",
        "image_url":   "",
        "scoring":     b.get("scoring") or {},
        "fiche_enrichie": b.get("fiche_enrichie") or {},
    }


def _search(query: str, n: int = 9) -> list[dict]:
    """Recherche via POST /rechercher (seul endpoint du backend) → mock en secours."""
    profil = st.session_state.get("profil_payload") or {
        "intention": st.session_state.get("profil_key", "rp"),
        "budget_max": 2_000_000,
    }
    try:
        r = requests.post(f"{API_URL}/rechercher",
                          json={**profil, "description_libre": query}, timeout=30)
        if r.ok:
            data = [_adapt(b) for b in r.json().get("resultats", [])]
            if data:
                return data
    except Exception:
        pass
    return mock_biens()


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    # Logo
    st.markdown("""
<div class="sidebar-logo">
  <div>
    <div class="sidebar-logo-title">NidBuyer</div>
    <div class="sidebar-logo-sub">Assistant Intelligent d'Aide<br>à la Décision Immobilière</div>
  </div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<hr style='border-color:rgba(255,255,255,0.08);margin:10px 0'>", unsafe_allow_html=True)

    # Sélection profil
    st.markdown("<p style='color:#64748b;font-size:0.78em;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:6px'>PROFIL ACHETEUR</p>", unsafe_allow_html=True)
    profil_options = list(PROFILS_CFG.keys())
    profil_labels  = {k: v["label"] for k, v in PROFILS_CFG.items()}
    selected = st.selectbox(
        "Profil",
        profil_options,
        format_func=lambda k: profil_labels[k],
        index=profil_options.index(st.session_state.profil_key),
        label_visibility="collapsed",
    )
    if selected != st.session_state.profil_key:
        st.session_state.profil_key  = selected
        st.session_state.analyse_done = False
        st.session_state.resultats    = []
        st.session_state.chat_msgs    = []
        st.rerun()

    st.markdown("<hr style='border-color:rgba(255,255,255,0.08);margin:10px 0'>", unsafe_allow_html=True)

    # Navigation
    st.markdown("<p style='color:#64748b;font-size:0.78em;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:6px'>NAVIGATION</p>", unsafe_allow_html=True)
    nav_items = [
        ("dashboard", "Tableau de bord"),
        ("biens",     "Biens recommandés"),
        ("analyse",   "Analyse IA"),
        ("chatbot",   "Chatbot IA"),
    ]
    for nav_key, nav_label in nav_items:
        if st.button(nav_label, key=f"nav_{nav_key}",
                     use_container_width=True):
            st.session_state.view = nav_key
            st.rerun()

    st.markdown("<hr style='border-color:rgba(255,255,255,0.08);margin:10px 0'>", unsafe_allow_html=True)

    # ── Formulaire ────────────────────────────────────────────────────────────
    st.markdown("<p style='color:#64748b;font-size:0.78em;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:6px'>CRITÈRES DE RECHERCHE</p>", unsafe_allow_html=True)

    budget = st.number_input("Budget max (€)", 50_000, 2_000_000, 300_000, 10_000)
    ville  = st.selectbox("Ville",
                           ["Toulon", "La Seyne-sur-Mer", "Hyères",
                            "Six-Fours-les-Plages", "Ollioules", "La Garde"])
    quartiers_toulon = [
        "Mourillon", "Centre-ville", "Sainte-Anne", "Le Cap Brun",
        "Saint-Jean-du-Var", "La Serinette", "Pont-du-Las", "Bon Rencontre",
        "Les Routes", "Saint-Roch", "La Rode", "Escaillon",
        "Sainte-Musse", "Siblas", "La Loubière", "Claret",
    ]
    qrt_list  = st.multiselect("Quartier(s)", quartiers_toulon,
                               placeholder="Choisissez un ou plusieurs quartiers")
    type_bien = st.selectbox("Type de bien",
                              ["Appartement", "Maison", "Studio", "T2", "T3", "T4", "T5+"])
    surf_min  = st.number_input("Surface min (m²)", 0, 500, 25)
    surf_max  = st.number_input("Surface max (m²)", 0, 1_000, 250)
    pieces_min = st.selectbox("Pièces min", ["Peu importe", "1", "2", "3", "4", "5+"])

    st.markdown("")
    lancer = st.button("Lancer l'analyse", type="primary", use_container_width=True)

    st.markdown("<hr style='border-color:rgba(255,255,255,0.08);margin:10px 0'>", unsafe_allow_html=True)
    ok_icon = "OK" if _backend_ok() else "HORS LIGNE"
    st.markdown(f"<p style='color:#475569;font-size:0.75em'>Backend {ok_icon} · <code>{API_URL}</code></p>",
                unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# LANCEMENT ANALYSE
# ══════════════════════════════════════════════════════════════════════════════

if lancer:
    full_q   = " ".join(filter(None, [type_bien, ville, *qrt_list,
                                       f"budget {budget}"]))
    payload  = {
        "intention":    st.session_state.profil_key,
        "budget_max":   budget,
        "surface_min":  surf_min,
        "quartiers":    qrt_list,
        "nb_pieces_min": None if pieces_min == "Peu importe" else int(pieces_min.replace("+", "")),
        "description_libre": "",
    }
    st.session_state.profil_payload = payload  # avant _search : le profil sert à /rechercher
    with st.spinner("Analyse en cours…"):
        biens = _search(full_q, n=9)

    st.session_state.resultats     = biens
    st.session_state.analyse_done  = True
    st.session_state.photo_analysis = {}
    st.session_state.view          = "dashboard"
    st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# ZONE PRINCIPALE
# ══════════════════════════════════════════════════════════════════════════════

biens   = st.session_state.resultats
payload = st.session_state.profil_payload or {
    "intention": st.session_state.profil_key, "budget_max": 300_000,
    "surface_min": 0, "quartiers": [], "nb_pieces_min": None, "description_libre": "",
}
view = st.session_state.view

# ── Header profil ─────────────────────────────────────────────────────────────
render_header(st.session_state.profil_key)

# ── État vide ─────────────────────────────────────────────────────────────────
if not st.session_state.analyse_done:
    st.markdown("""
<div class="empty-state" style="margin-top:40px">
  <div class="empty-icon">[ recherche ]</div>
  <div class="empty-text" style="font-size:1.1em;font-weight:600;color:#0b1f3a">
    Renseignez vos critères dans la sidebar et cliquez sur <strong>Lancer l'analyse</strong>
  </div>
  <div class="empty-text" style="margin-top:8px">
    L'IA analysera les annonces et vous fournira une fiche décision complète.
  </div>
</div>""", unsafe_allow_html=True)
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# VUE : TABLEAU DE BORD
# ══════════════════════════════════════════════════════════════════════════════

if view == "dashboard":
    st.markdown('<div class="sec-title">Indicateurs clés du marché</div>', unsafe_allow_html=True)
    render_kpis(biens)

    st.markdown("")

    tab_ana, tab_score, tab_fiche, tab_photos = st.tabs([
        "Analyses et Statistiques",
        "Scoring immobilier",
        "Fiche Décision IA",
        "Analyse Photos IA",
    ])

    with tab_ana:
        render_charts(biens)

    with tab_score:
        render_scoring(biens)

    with tab_fiche:
        render_fiche_decision(biens, st.session_state.profil_key)

    with tab_photos:
        render_photos_analysis(st.session_state.photo_analysis)

    st.markdown("")
    st.markdown('<div class="sec-title">Biens recommandés (aperçu)</div>', unsafe_allow_html=True)
    render_biens(biens[:3])
    if len(biens) > 3:
        if st.button(f"Voir tous les biens ({len(biens)})", key="voir_tous"):
            st.session_state.view = "biens"
            st.rerun()

    st.markdown("")
    st.markdown('<div class="sec-title">Chatbot IA</div>', unsafe_allow_html=True)
    render_chatbot(payload, API_URL, _search)

# ══════════════════════════════════════════════════════════════════════════════
# VUE : BIENS RECOMMANDÉS
# ══════════════════════════════════════════════════════════════════════════════

elif view == "biens":
    st.markdown(f'<div class="sec-title">Biens recommandés — {len(biens)} résultat(s)</div>',
                unsafe_allow_html=True)
    render_kpis(biens)
    st.markdown("")
    render_biens(biens)

# ══════════════════════════════════════════════════════════════════════════════
# VUE : ANALYSE IA
# ══════════════════════════════════════════════════════════════════════════════

elif view == "analyse":
    st.markdown('<div class="sec-title">Analyses et Statistiques du marché</div>',
                unsafe_allow_html=True)
    render_charts(biens)

    st.markdown("")
    st.markdown('<div class="sec-title">Scoring immobilier</div>', unsafe_allow_html=True)
    render_scoring(biens)

    st.markdown("")
    st.markdown('<div class="sec-title">Fiche Décision IA</div>', unsafe_allow_html=True)
    render_fiche_decision(biens, st.session_state.profil_key)

# ══════════════════════════════════════════════════════════════════════════════
# VUE : CHATBOT
# ══════════════════════════════════════════════════════════════════════════════

elif view == "chatbot":
    st.markdown('<div class="sec-title">Chatbot IA — Posez vos questions</div>',
                unsafe_allow_html=True)
    render_chatbot(payload, API_URL, _search)
