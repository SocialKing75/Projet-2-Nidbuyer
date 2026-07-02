"""Composants réutilisables NidBuyer."""
from __future__ import annotations

import random
from typing import Optional

import streamlit as st

try:
    import plotly.express as px
    import plotly.graph_objects as go
    import pandas as pd
    PLOTLY = True
except ImportError:
    PLOTLY = False


# ── Constantes marché ────────────────────────────────────────────────────────
MEDIANE_DVF: dict[str, float] = {
    "Mourillon": 3_850,
    "Centre-ville": 3_400,
    "Sainte-Anne": 3_100,
    "La Seyne-sur-Mer": 2_800,
    "Hyères": 3_200,
    "Le Pradet": 3_000,
    "Six-Fours-les-Plages": 3_050,
    "default": 3_200,
}

PROFILS_CFG: dict[str, dict] = {
    "rp": {
        "icon": "RP", "label": "Résidence Principale",
        "desc": "Trouvez le bien idéal pour votre résidence principale.",
        "couleur": "#3b82f6",
    },
    "investissement": {
        "icon": "INV", "label": "Investisseur Locatif",
        "desc": "Identifiez les opportunités à fort rendement.",
        "couleur": "#22c55e",
    },
    "rs": {
        "icon": "RS", "label": "Résidence Secondaire",
        "desc": "Votre pied-à-terre idéal sur la Côte d'Azur.",
        "couleur": "#14b8a6",
    },
    "mixte": {
        "icon": "MIX", "label": "Immeuble Mixte",
        "desc": "Analysez un immeuble avec plusieurs usages.",
        "couleur": "#8b5cf6",
    },
}


# ── Données mock Toulon ──────────────────────────────────────────────────────
def mock_biens() -> list[dict]:
    """Données de démo quand ChromaDB/Supabase est vide."""
    return [
        {"type": "Appartement T3", "prix": 245_000, "surface": 68, "quartier": "Mourillon",
         "ville": "Toulon", "nb_pieces": 3, "dpe": "C",
         "description": "Bel appartement lumineux proche de la mer.",
         "url_source": "https://www.bienici.com", "image_url": ""},
        {"type": "Appartement T2", "prix": 155_000, "surface": 42, "quartier": "Centre-ville",
         "ville": "Toulon", "nb_pieces": 2, "dpe": "D",
         "description": "T2 idéal investissement, centre historique.",
         "url_source": "https://www.bienici.com", "image_url": ""},
        {"type": "Maison T5", "prix": 390_000, "surface": 120, "quartier": "Sainte-Anne",
         "ville": "Toulon", "nb_pieces": 5, "dpe": "B",
         "description": "Maison avec jardin, calme et résidentiel.",
         "url_source": "https://www.bienici.com", "image_url": ""},
        {"type": "Appartement T4", "prix": 310_000, "surface": 88, "quartier": "Mourillon",
         "ville": "Toulon", "nb_pieces": 4, "dpe": "C",
         "description": "Grand T4 avec vue mer partielle.",
         "url_source": "https://www.bienici.com", "image_url": ""},
        {"type": "Studio T1", "prix": 89_000, "surface": 24, "quartier": "Centre-ville",
         "ville": "Toulon", "nb_pieces": 1, "dpe": "E",
         "description": "Studio idéal primo-accédant ou investisseur.",
         "url_source": "https://www.bienici.com", "image_url": ""},
        {"type": "Appartement T3", "prix": 195_000, "surface": 72, "quartier": "La Seyne-sur-Mer",
         "ville": "La Seyne-sur-Mer", "nb_pieces": 3, "dpe": "C",
         "description": "T3 rénové proche commodités.",
         "url_source": "https://www.bienici.com", "image_url": ""},
    ]


# ── Scoring ──────────────────────────────────────────────────────────────────
def calc_pm2(bien: dict) -> Optional[float]:
    try:
        p = float(str(bien.get("prix") or "0").replace(" ", "").replace(" ", ""))
        s = float(str(bien.get("surface") or "0").replace("m²", "").replace("m2", "").strip())
        return round(p / s) if p > 0 and s > 0 else None
    except Exception:
        return None


def score_info(pm2: Optional[float], quartier: str = "default") -> dict:
    """Retourne label, css_class, score/100, color, opportunite."""
    mediane = MEDIANE_DVF.get(quartier, MEDIANE_DVF["default"])
    if pm2 is None:
        return {"label": "N/D", "css": "sb-nd", "score": 0,
                "color": "#94a3b8", "opp": "N/D", "ecart": 0, "mediane": mediane}
    ecart = round((pm2 - mediane) / mediane * 100, 1)
    score = max(0, min(100, round(50 - ecart)))
    if score >= 80:
        label, css, color, opp = "Excellent",  "sb-excellent", "#22c55e", "Forte"
    elif score >= 65:
        label, css, color, opp = "Très bon",   "sb-tres-bon",  "#4ade80", "Forte"
    elif score >= 50:
        label, css, color, opp = "Bon",         "sb-bon",       "#fbbf24", "Moyenne"
    elif score >= 35:
        label, css, color, opp = "Moyen",       "sb-moyen",     "#f97316", "Faible"
    else:
        label, css, color, opp = "Risqué",      "sb-risque",    "#ef4444", "Faible"
    return {"label": label, "css": css, "score": score,
            "color": color, "opp": opp, "ecart": ecart, "mediane": mediane}


# ── Header profil ─────────────────────────────────────────────────────────────
def render_header(profil_key: str) -> None:
    cfg = PROFILS_CFG.get(profil_key, PROFILS_CFG["rp"])
    st.markdown(f"""
<div class="prof-header">
  <div class="prof-header-icon">{cfg['icon']}</div>
  <div>
    <div class="prof-header-name">{cfg['label']}</div>
    <div class="prof-header-desc">{cfg['desc']}</div>
  </div>
</div>""", unsafe_allow_html=True)


# ── KPIs ─────────────────────────────────────────────────────────────────────
def render_kpis(biens: list[dict]) -> None:
    prix_l, pm2_l, score_l = [], [], []
    for b in biens:
        try:
            p = float(str(b.get("prix") or "0").replace(" ", "").replace(" ", ""))
            if p > 0:
                prix_l.append(p)
        except Exception:
            pass
        v = calc_pm2(b)
        if v:
            pm2_l.append(v)
            score_l.append(score_info(v, b.get("quartier", "default"))["score"])

    def eur(x: float) -> str:
        return f"{int(x):,}".replace(",", " ") + " €"

    avg_pm2 = sum(pm2_l) / len(pm2_l) if pm2_l else None
    mediane_ref = MEDIANE_DVF["default"]

    kpis = [
        ("N", str(len(biens)),
         "Biens trouvés", "blue"),
        ("EUR", eur(sum(prix_l) / len(prix_l)) if prix_l else "N/D",
         "Prix moyen", "orange"),
        ("/m2", (eur(sum(pm2_l) / len(pm2_l)) + "/m²") if pm2_l else "N/D",
         "Prix moyen / m²", "purple"),
        ("DVF", f"{mediane_ref:,} €/m²".replace(",", " "),
         "Médiane DVF Toulon", "teal"),
        ("pts", f"{round(sum(score_l)/len(score_l))}/100" if score_l else "N/D",
         "Score moyen", "rose"),
    ]

    cols = st.columns(len(kpis))
    for col, (icon, val, label, color) in zip(cols, kpis):
        with col:
            st.markdown(f"""
<div class="kpi-card {color}">
  <div class="kpi-icon">{icon}</div>
  <div class="kpi-value">{val}</div>
  <div class="kpi-label">{label}</div>
</div>""", unsafe_allow_html=True)


# ── Graphiques Plotly ─────────────────────────────────────────────────────────
def render_charts(biens: list[dict]) -> None:
    if not PLOTLY:
        st.info("Plotly non installé — `pip install plotly`")
        return
    if not biens:
        return

    rows = []
    for b in biens:
        pm2 = calc_pm2(b)
        try:
            rows.append({
                "prix":     float(str(b.get("prix") or "0").replace(" ", "").replace(" ", "")),
                "surface":  float(str(b.get("surface") or "0").replace("m²", "").replace("m2", "").strip()),
                "quartier": str(b.get("quartier") or "Inconnu"),
                "type":     str(b.get("type") or "Bien"),
                "pm2":      pm2 or 0,
            })
        except Exception:
            pass

    df = pd.DataFrame([r for r in rows if r["prix"] > 0])
    if df.empty:
        return

    PAL = px.colors.qualitative.Set2
    BG  = dict(paper_bgcolor="white", plot_bgcolor="#f8fafc",
               margin=dict(t=36, b=16, l=16, r=16))

    tab1, tab2, tab3 = st.tabs(["Distribution", "Par quartier", "Surface vs Prix"])

    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            fig = px.histogram(df, x="prix", nbins=12, title="Répartition des prix",
                               labels={"prix": "Prix (€)"},
                               color_discrete_sequence=["#0b1f3a"])
            fig.update_layout(**BG)
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            tc = df["type"].value_counts().reset_index()
            tc.columns = ["type", "n"]
            fig2 = px.pie(tc, names="type", values="n", title="Types de biens",
                          color_discrete_sequence=px.colors.qualitative.Pastel)
            fig2.update_layout(paper_bgcolor="white", margin=dict(t=36, b=16, l=16, r=16))
            st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        c1, c2 = st.columns(2)
        with c1:
            qc = df["quartier"].value_counts().reset_index()
            qc.columns = ["quartier", "n"]
            fig3 = px.bar(qc, x="quartier", y="n", title="Biens par quartier",
                          color="quartier", color_discrete_sequence=PAL)
            fig3.update_layout(showlegend=False, **BG)
            st.plotly_chart(fig3, use_container_width=True)
        with c2:
            dfp = df[df["pm2"] > 0]
            if not dfp.empty:
                fig4 = px.box(dfp, x="quartier", y="pm2",
                              title="Prix/m² par quartier",
                              labels={"pm2": "€/m²", "quartier": "Quartier"},
                              color="quartier", color_discrete_sequence=PAL)
                fig4.update_layout(showlegend=False, **BG)
                st.plotly_chart(fig4, use_container_width=True)

    with tab3:
        dfs = df[(df["surface"] > 0) & (df["prix"] > 0)]
        if not dfs.empty:
            fig5 = px.scatter(dfs, x="surface", y="prix",
                              color="quartier",
                              size=dfs["pm2"].clip(lower=1),
                              title="Surface vs Prix",
                              labels={"surface": "Surface (m²)", "prix": "Prix (€)"},
                              color_discrete_sequence=PAL,
                              hover_data=["quartier", "pm2"])
            fig5.update_layout(**BG)
            st.plotly_chart(fig5, use_container_width=True)


# ── Gauge scoring ─────────────────────────────────────────────────────────────
def render_scoring(biens: list[dict]) -> None:
    if not PLOTLY or not biens:
        return

    pm2_vals = [(calc_pm2(b), b.get("quartier", "default")) for b in biens]
    pm2_vals = [(v, q) for v, q in pm2_vals if v is not None]
    if not pm2_vals:
        st.warning("Données insuffisantes pour le scoring.")
        return

    avg_pm2 = sum(v for v, _ in pm2_vals) / len(pm2_vals)
    first_q  = pm2_vals[0][1]
    info     = score_info(avg_pm2, first_q)

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=info["score"],
        title={"text": f"Score global · <b>{info['label']}</b>",
               "font": {"size": 14, "color": "#0b1f3a"}},
        number={"suffix": "/100", "font": {"color": info["color"], "size": 30}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#cbd5e1"},
            "bar": {"color": info["color"], "thickness": 0.22},
            "bgcolor": "white",
            "steps": [
                {"range": [0, 35],  "color": "#fee2e2"},
                {"range": [35, 50], "color": "#ffedd5"},
                {"range": [50, 65], "color": "#fef3c7"},
                {"range": [65, 80], "color": "#dcfce7"},
                {"range": [80, 100],"color": "#d1fae5"},
            ],
            "threshold": {"line": {"color": "#0b1f3a", "width": 3},
                          "thickness": 0.75, "value": 50},
        },
    ))
    fig.update_layout(height=230, paper_bgcolor="white",
                      margin=dict(t=60, b=10, l=20, r=20))
    st.plotly_chart(fig, use_container_width=True)

    st.progress(info["score"] / 100,
                text=f"Prix moy/m² : {int(avg_pm2):,} €  ·  Médiane DVF : {int(info['mediane']):,} €  ·  Écart : {info['ecart']:+.1f}%".replace(",", " "))

    c1, c2, c3 = st.columns(3)
    c1.metric("Opportunité", info["opp"])
    c2.metric("Écart vs médiane", f"{info['ecart']:+.1f}%")
    c3.metric("Score", f"{info['score']}/100")


# ── Fiche décision IA ─────────────────────────────────────────────────────────
def render_fiche_decision(biens: list[dict], profil_key: str) -> None:
    if not biens:
        return

    pm2_vals = [calc_pm2(b) for b in biens]
    pm2_vals = [v for v in pm2_vals if v is not None]
    avg_pm2  = int(sum(pm2_vals) / len(pm2_vals)) if pm2_vals else None
    info     = score_info(avg_pm2) if avg_pm2 else score_info(None)
    ecart    = info["ecart"]

    if info["score"] >= 65:
        opp_txt  = f"Opportunité {info['opp'].lower()} — bien {abs(ecart):.1f}% sous la médiane DVF."
        pts_forts = "Prix attractif par rapport au marché · Bonne liquidité potentielle."
        neg_txt  = f"Marge de négociation estimée à {max(1, abs(ecart)-5):.0f}–{abs(ecart):.0f}%."
        reco     = "Agir rapidement. Ce niveau de prix est rare sur ce marché."
    elif info["score"] >= 45:
        opp_txt  = "Prix dans la norme du marché — opportunité modérée."
        pts_forts = "Cohérence prix/marché · Négociation possible de 2–4%."
        neg_txt  = "Négociation possible de 2–4%. Demander la dernière estimation."
        reco     = "Vérifier l'état général et les charges avant offre."
    else:
        opp_txt  = f"Prix {ecart:.1f}% au-dessus de la médiane DVF. Prudence."
        pts_forts = "Localisation ou prestations à valider pour justifier l'écart."
        neg_txt  = f"Peu de marge de négociation. Écart de {ecart:.1f}%."
        reco     = "Comparer avec des biens similaires avant de décider."

    profil_conseil = {
        "rp":            "Résidence principale : privilégiez qualité de vie et liquidité.",
        "investissement": "Investissement : calculez rendement net après charges et fiscalité.",
        "rs":            "Résidence secondaire : évaluez les coûts de gestion hors-saison.",
        "mixte":         "Immeuble mixte : vérifiez la conformité des baux commerciaux.",
    }.get(profil_key, "")

    st.markdown(f"""
<div class="dec-card">
  <h3>Fiche Décision IA</h3>
  <div class="dec-row">
    <div class="dec-lbl">Opportunité</div>
    <div class="dec-val">{opp_txt}</div>
  </div>
  <div class="dec-row">
    <div class="dec-lbl">Points forts</div>
    <div class="dec-val">{pts_forts}</div>
  </div>
  <div class="dec-row">
    <div class="dec-lbl">Point d'attention</div>
    <div class="dec-val">Vérifier l'état du bien, les charges et le DPE.</div>
  </div>
  <div class="dec-row">
    <div class="dec-lbl">Conseil négociation</div>
    <div class="dec-val">{neg_txt}</div>
  </div>
  <div class="dec-row">
    <div class="dec-lbl">Recommandation</div>
    <div class="dec-val">{reco}</div>
  </div>
  <div class="dec-row">
    <div class="dec-lbl">Conseil profil</div>
    <div class="dec-val">{profil_conseil}</div>
  </div>
</div>""", unsafe_allow_html=True)


# ── Analyse photos IA (simulée, prête pour IA Vision) ───────────────────────
def analyser_photos(photos: list) -> dict:
    """
    Simulation d'analyse IA Vision.
    Remplacer le corps de cette fonction par un appel à l'API Vision réelle.
    """
    if not photos:
        return {}
    etats = ["Excellent", "Bon", "Correct", "À rénover"]
    etat  = random.choice(etats[:3])
    travaux = etat in ["Correct", "À rénover"]
    tranches = {"0–5 000 €": 5_000, "5 000–20 000 €": 20_000,
                "20 000–50 000 €": 50_000, "> 50 000 €": 80_000}
    cout = random.choice(list(tranches)) if travaux else "Aucun"
    return {
        "nb_photos":            len(photos),
        "etat_general":         etat,
        "score_presentation":   random.randint(65, 95),
        "travaux_detectes":     travaux,
        "cout_travaux":         cout,
        "defauts":              (["Peinture à rafraîchir", "Cuisine ancienne"] if travaux
                                 else ["Aucun défaut visible"]),
        "resume":               (
            f"État général **{etat}**. "
            + ("Travaux de rafraîchissement conseillés."
               if travaux else "Aucun travail majeur nécessaire.")
        ),
    }


def render_photos_analysis(photo_data: dict) -> None:
    if not photo_data:
        st.markdown("""
<div class="empty-state">
  <div class="empty-icon">[ photo ]</div>
  <div class="empty-text">Uploadez des photos dans le formulaire pour activer l'analyse IA.</div>
</div>""", unsafe_allow_html=True)
        return

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("État général",          photo_data.get("etat_general", "N/D"))
    c2.metric("Score présentation",    f"{photo_data.get('score_presentation', 0)}/100")
    c3.metric("Travaux estimés",       photo_data.get("cout_travaux", "N/D"))
    c4.metric("Photos analysées",      str(photo_data.get("nb_photos", 0)))

    st.markdown("---")
    st.write("**Défauts observés :**", "  ·  ".join(photo_data.get("defauts", [])))
    st.write("**Résumé IA :**", photo_data.get("resume", ""))
    st.info("Module Vision IA — données simulées. Remplacez `analyser_photos()` dans `components.py` par votre API Vision.")


# ── Cartes biens ──────────────────────────────────────────────────────────────
def render_biens(biens: list[dict]) -> None:
    if not biens:
        st.markdown("""
<div class="empty-state">
  <div class="empty-icon">[ recherche ]</div>
  <div class="empty-text">Aucun bien trouvé. Affinez vos critères et relancez l'analyse.</div>
</div>""", unsafe_allow_html=True)
        return

    for i in range(0, len(biens), 3):
        cols = st.columns(3)
        for j, bien in enumerate(biens[i:i + 3]):
            pm2   = calc_pm2(bien)
            info  = score_info(pm2, bien.get("quartier", "default"))
            prix  = bien.get("prix")
            surf  = bien.get("surface")
            type_b = bien.get("type", "Bien")
            qrt   = bien.get("quartier", "")
            ville = bien.get("ville", "Toulon")
            url   = bien.get("url_source", "")
            dpe   = bien.get("dpe", "")
            pieces = bien.get("nb_pieces", "")

            try:
                prix_fmt = f"{int(float(str(prix).replace(' ', '').replace(' ', ''))):,} €".replace(",", " ")
            except Exception:
                prix_fmt = "Prix NC"
            pm2_fmt  = f"{int(pm2):,} €/m²".replace(",", " ") if pm2 else "N/D"
            surf_fmt = f"{surf} m²" if surf else "N/D"
            tags = [t for t in [surf_fmt, (f"{pieces} p." if pieces else ""), dpe] if t]

            lien = (f'<div class="bien-link"><a href="{url}" target="_blank">Voir l\'annonce</a></div>'
                    if url else "")
            tags_html = "".join(f'<span class="bien-tag">{t}</span>' for t in tags)

            with cols[j]:
                st.markdown(f"""
<div class="bien-card">
  <div class="bien-img">[ photo ]</div>
  <div class="bien-body">
    <div class="bien-prix">{prix_fmt}</div>
    <div class="bien-titre">{type_b}</div>
    <div class="bien-loc">{qrt}{', ' + ville if ville else ''}</div>
    <div class="bien-tags">{tags_html}</div>
    <div class="bien-score">
      <span class="sbadge {info['css']}">{info['label']}</span>
      <span style="color:#94a3b8;font-size:0.78em;margin-left:6px">{pm2_fmt}</span>
    </div>
    {lien}
  </div>
</div>""", unsafe_allow_html=True)


# ── Chatbot ───────────────────────────────────────────────────────────────────
def render_chatbot(profil_payload: dict, api_url: str, search_fn) -> None:
    if "chat_msgs" not in st.session_state:
        st.session_state.chat_msgs = [{
            "role": "assistant",
            "content": "Bonjour ! Posez-moi une question sur votre projet immobilier à Toulon.",
        }]

    html = '<div class="chat-wrap">'
    for msg in st.session_state.chat_msgs:
        if msg["role"] == "user":
            html += f'<div class="chat-user">{msg["content"]}</div>'
        else:
            html += f'<div class="chat-bot">{msg["content"]}</div>'
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

    c_in, c_btn = st.columns([5, 1])
    with c_in:
        question = st.text_input("Votre question", placeholder="Ex : Quels quartiers pour un T3 à 280 000 € ?",
                                 key="chat_question", label_visibility="collapsed")
    with c_btn:
        send = st.button("Envoyer", key="chat_send", use_container_width=True)

    if send and question:
        st.session_state.chat_msgs.append({"role": "user", "content": question})
        hist = [{"role": m["role"], "content": m["content"]}
                for m in st.session_state.chat_msgs[:-1]]
        with st.spinner("Analyse…"):
            rep = _get_chat_response(question, profil_payload, hist, api_url, search_fn)
        st.session_state.chat_msgs.append({"role": "assistant", "content": rep})
        st.rerun()


def _get_chat_response(question: str, profil: dict, hist: list,
                       api_url: str, search_fn) -> str:
    try:
        import requests as _req  # noqa: PLC0415
        r = _req.post(f"{api_url}/chat",
                      json={"question": question, "profil": profil, "historique": hist},
                      timeout=45)
        if r.ok:
            data = r.json()
            rep = data.get("reponse") or data.get("response") or ""
            if rep:
                return rep
    except Exception:
        pass
    try:
        results = search_fn(question, n=3)
        if results:
            quartiers = list({b.get("quartier", "") for b in results if b.get("quartier")})
            return (f"J'ai trouvé {len(results)} bien(s) correspondant à votre recherche. "
                    f"Quartiers identifiés : {', '.join(quartiers) or 'variés'}.")
    except Exception:
        pass
    return "Je n'ai pas pu analyser votre demande. Vérifiez que le backend est démarré."
