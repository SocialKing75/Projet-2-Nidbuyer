"""
SuperIA — Votre acheteur IA à Toulon
Interface Streamlit pour explorer des biens immobiliers selon votre profil
"""
import streamlit as st
import requests

API_URL = "http://localhost:8000"

# Configuration page
st.set_page_config(
    page_title="SuperIA - Accueil",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .profile-card {
        border: 2px solid #e1e4e8;
        border-radius: 8px;
        padding: 20px;
        margin: 10px 0;
        background-color: #f6f8fa;
    }
    .profile-card.active {
        border-color: #0366d6;
        background-color: #f0f7ff;
    }
    .fiche-decision {
        background-color: #f5f5f5;
        border-left: 4px solid #0366d6;
        padding: 15px;
        border-radius: 4px;
        margin: 10px 0;
    }
    .score-excellent { color: #28a745; font-weight: bold; }
    .score-bon { color: #ffc107; font-weight: bold; }
    .score-moyen { color: #fd7e14; font-weight: bold; }
    .score-mauvais { color: #dc3545; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- Session state initialization ---
if "page" not in st.session_state:
    st.session_state.page = "accueil"
if "profil" not in st.session_state:
    st.session_state.profil = None
if "resultats_recherche" not in st.session_state:
    st.session_state.resultats_recherche = None
if "criteres_formulaire" not in st.session_state:
    st.session_state.criteres_formulaire = {}

# --- Navigation ---
def goto_page(page_name, profil=None):
    st.session_state.page = page_name
    if profil:
        st.session_state.profil = profil


# ============================================================================
# PAGE D'ACCUEIL
# ============================================================================
def afficher_accueil():
    st.title("SuperIA")
    st.markdown("### Votre acheteur IA à Toulon")
    st.markdown("""
    Bienvenue sur **SuperIA** — l'IA qui comprend votre besoin immobilier et trouve le bien idéal pour vous.

    Nous proposons 4 profils d'achat différents. Sélectionnez le vôtre pour explorer les biens qui vous correspondent.
    """)

    st.markdown("---")
    st.markdown("## Quel est votre projet immobilier ?")

    cols = st.columns(2)

    # Résidence Principale
    with cols[0]:
        st.markdown("""
        <div class="profile-card">
            <h3>Résidence Principale</h3>
            <p>Vous cherchez un bien pour y habiter en tant que résidence principale.</p>
            <p><strong>Cas d'usage:</strong> Famille, jeune professionnel, couple cherchant un foyer.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Commencer avec RP", key="btn_rp", use_container_width=True):
            goto_page("recherche", "rp")
            st.rerun()

    # Investissement Locatif
    with cols[1]:
        st.markdown("""
        <div class="profile-card">
            <h3>Investissement Locatif</h3>
            <p>Vous cherchez un bien pour générer des revenus en location.</p>
            <p><strong>Cas d'usage:</strong> Rendement, diversification, patrimoine.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Commencer avec INV", key="btn_inv", use_container_width=True):
            goto_page("recherche", "investissement")
            st.rerun()

    cols = st.columns(2)

    # Résidence Secondaire
    with cols[0]:
        st.markdown("""
        <div class="profile-card">
            <h3>Résidence Secondaire</h3>
            <p>Vous cherchez un bien pour les vacances et loisirs.</p>
            <p><strong>Cas d'usage:</strong> Maison de vacances, pied-à-terre, refuge.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Commencer avec RS", key="btn_rs", use_container_width=True):
            goto_page("recherche", "rs")
            st.rerun()

    # Immeuble Mixte
    with cols[1]:
        st.markdown("""
        <div class="profile-card">
            <h3>Immeuble Mixte</h3>
            <p>Vous cherchez un immeuble avec usage résidentiel et commercial.</p>
            <p><strong>Cas d'usage:</strong> Investisseur averti, rendement mixte.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Commencer avec MIX", key="btn_mix", use_container_width=True):
            goto_page("recherche", "mixte")
            st.rerun()


# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================
def faire_recherche(profil_data):
    """Appelle l'API /rechercher et retourne les résultats."""
    try:
        response = requests.post(f"{API_URL}/rechercher", json=profil_data, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Erreur API: {response.status_code}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("Impossible de se connecter à l'API. Assurez-vous que le backend est en cours d'exécution.")
        return None
    except Exception as e:
        st.error(f"Erreur: {str(e)}")
        return None


def afficher_fiche_bien(bien, idx):
    """Affiche une fiche complète enrichie avec opportunités, risques, conseil."""
    with st.container():
        st.markdown(f"### {idx}. {bien['titre']}")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Prix", f"{bien['prix']:,}€")
        with col2:
            st.metric("Surface", f"{bien['surface']}m²")
        with col3:
            st.metric("Pièces", bien['pieces'])

        score = bien['scoring']
        fiche = bien.get('fiche_enrichie', {})
        score_color = "score-excellent" if score['score'] >= 75 else "score-bon" if score['score'] >= 60 else "score-moyen" if score['score'] >= 40 else "score-mauvais"

        st.markdown(f"""
        <div class="fiche-decision">
        <div class="{score_color}">Score d'opportunité: {score['score']}/100 — {score['label']}</div>

        **Localisation:** {bien['quartier']}
        **€/m²:** {score['prix_m2']:.0f}€/m² (écart médiane: {score['ecart_pct']:+.1f}%)
        **Type:** {bien['type']}

        **Description:**
        {bien['description']}
        """, unsafe_allow_html=True)

        if fiche.get('opportunites'):
            st.success("**Opportunités:**")
            for opp in fiche['opportunites']:
                st.write(f"• {opp}")

        if fiche.get('risques'):
            st.warning("**Risques:**")
            for risque in fiche['risques']:
                st.write(f"• {risque}")

        if fiche.get('conseil'):
            st.info(f"**Conseil:** {fiche['conseil']}")

        if bien.get('rendement'):
            rend = bien['rendement']
            st.write(f"**Rendement estimé:** {rend['rendement_brut_pct']:.2f}% brut | {rend['rendement_net_pct']:.2f}% net")
            st.write(f"(Loyer estimé: {rend['loyer_mensuel_estime']:.0f}€/mois)")

        st.markdown("---")
        st.markdown("</div>", unsafe_allow_html=True)


# ============================================================================
# PAGE RECHERCHE AVEC FORMULAIRES PAR PROFIL
# ============================================================================
def afficher_recherche():
    profil = st.session_state.profil

    if not profil:
        st.warning("Aucun profil sélectionné")
        if st.button("Retour à l'accueil"):
            goto_page("accueil")
            st.rerun()
        return

    # Header avec bouton retour
    col1, col2 = st.columns([0.9, 0.1])
    with col1:
        titles = {
            "rp": "Résidence Principale",
            "investissement": "Investissement Locatif",
            "rs": "Résidence Secondaire",
            "mixte": "Immeuble Mixte"
        }
        st.title(titles.get(profil, "Recherche"))
    with col2:
        if st.button("Accueil", key="btn_back_accueil"):
            goto_page("accueil")
            st.rerun()

    st.markdown("---")

    # Formulaire adapté au profil
    col_form, col_results = st.columns([1, 2])

    with col_form:
        st.markdown("### Mes critères de recherche")

        if profil == "rp":
            criteres = formulaire_rp()
        elif profil == "investissement":
            criteres = formulaire_investissement()
        elif profil == "rs":
            criteres = formulaire_rs()
        elif profil == "mixte":
            criteres = formulaire_mixte()

        if st.button("Lancer la recherche", type="primary", use_container_width=True):
            with st.spinner("Recherche en cours..."):
                resultats = faire_recherche(criteres)
                if resultats:
                    st.session_state.resultats_recherche = resultats
                    st.rerun()

    with col_results:
        st.markdown("### Résultats de recherche")

        if st.session_state.resultats_recherche is None:
            st.info("Les biens correspondant à vos critères s'afficheront ici.")
        else:
            resultats = st.session_state.resultats_recherche
            biens = resultats.get("resultats", [])

            if not biens:
                st.warning("Aucun bien ne correspond à vos critères.")
            else:
                st.success(f"{len(biens)} bien(s) trouvé(s)")

                # Filtres et tri dynamiques
                col_tri, col_filtre = st.columns(2)
                with col_tri:
                    tri = st.selectbox(
                        "Trier par:",
                        ["Score (meilleur)", "Prix (croissant)", "Prix (décroissant)", "Surface (grand)"],
                        key="tri_biens"
                    )

                with col_filtre:
                    filtre_score = st.slider(
                        "Score minimum:",
                        min_value=0,
                        max_value=100,
                        value=40,
                        step=5,
                        key="filtre_score"
                    )

                # Appliquer le tri et le filtre
                biens_filtres = [b for b in biens if b['scoring']['score'] >= filtre_score]

                if tri == "Score (meilleur)":
                    biens_filtres.sort(key=lambda b: b['scoring']['score'], reverse=True)
                elif tri == "Prix (croissant)":
                    biens_filtres.sort(key=lambda b: b['prix'])
                elif tri == "Prix (décroissant)":
                    biens_filtres.sort(key=lambda b: b['prix'], reverse=True)
                elif tri == "Surface (grand)":
                    biens_filtres.sort(key=lambda b: b['surface'], reverse=True)

                if not biens_filtres:
                    st.warning("Aucun bien ne correspond aux filtres appliqués.")
                else:
                    st.info(f"Affichage: {len(biens_filtres)}/{len(biens)} bien(s)")
                    for idx, bien in enumerate(biens_filtres, 1):
                        afficher_fiche_bien(bien, idx)


# ============================================================================
# FORMULAIRES PAR PROFIL
# ============================================================================
def formulaire_rp():
    """Formulaire pour Résidence Principale avec filtres dynamiques"""
    budget = st.number_input(
        "Budget max (€)",
        min_value=50_000,
        max_value=2_000_000,
        value=300_000,
        step=10_000
    )
    surface_min = st.number_input(
        "Surface minimale (m²)",
        min_value=0,
        max_value=300,
        value=60
    )

    col1, col2 = st.columns(2)
    with col1:
        nb_pieces = st.selectbox(
            "Nombre de pièces",
            ["Peu importe", "T2", "T3", "T4", "T5+"]
        )
    with col2:
        luminosite_min = st.slider(
            "Luminosité minimale",
            min_value=1,
            max_value=5,
            value=3,
            step=1
        )

    localisation = st.multiselect(
        "Localisations préférées",
        ["Centre-ville", "Quartiers résidentiels", "Proche mer", "Proche transports", "Calme"],
        default=["Centre-ville"]
    )
    description = st.text_area(
        "Décrivez votre bien idéal",
        placeholder="Ex: T3 calme, proche mer, lumineux, avec parking...",
        value=""
    )

    return {
        "intention": "rp",
        "budget_max": budget,
        "surface_min": surface_min,
        "quartiers": localisation,
        "description_libre": f"{description} luminosite_min:{luminosite_min}"
    }


def formulaire_investissement():
    """Formulaire pour Investissement Locatif avec filtres dynamiques"""
    budget = st.number_input(
        "Budget d'investissement (€)",
        min_value=100_000,
        max_value=5_000_000,
        value=400_000,
        step=10_000
    )

    col1, col2 = st.columns(2)
    with col1:
        rendement_min = st.slider(
            "Rendement attendu (%)",
            min_value=2.0,
            max_value=10.0,
            value=5.0,
            step=0.5
        )
    with col2:
        score_min = st.slider(
            "Score d'opportunité min",
            min_value=0,
            max_value=100,
            value=50,
            step=10
        )

    type_bien = st.multiselect(
        "Type de bien préféré",
        ["Studio", "T2", "T3", "T4", "T5+", "Immeuble"],
        default=["T2", "T3"]
    )
    localisation = st.multiselect(
        "Zones avec bon potentiel locatif",
        ["Centre-ville", "Quartiers étudiants", "Proche transport", "Toulon centre"],
        default=["Centre-ville"]
    )
    description = st.text_area(
        "Stratégie d'investissement",
        placeholder="Ex: Bien avec potentiel de location courte durée, près des universités...",
        value=""
    )

    return {
        "intention": "investissement",
        "budget_max": budget,
        "surface_min": 0,
        "quartiers": localisation,
        "description_libre": f"{description} rendement_min:{rendement_min}% types:{','.join(type_bien)}"
    }


def formulaire_rs():
    """Formulaire pour Résidence Secondaire avec filtres dynamiques"""
    budget = st.number_input(
        "Budget max (€)",
        min_value=50_000,
        max_value=2_000_000,
        value=200_000,
        step=10_000
    )
    surface_min = st.number_input(
        "Surface minimale (m²)",
        min_value=0,
        max_value=300,
        value=40
    )

    col1, col2 = st.columns(2)
    with col1:
        type_loc = st.selectbox(
            "Type de localisation",
            ["Plage / Côte", "Montagne", "Campagne", "Petit village", "Peu importe"]
        )
    with col2:
        distance_max = st.slider(
            "Distance max de Toulon (km)",
            min_value=0,
            max_value=500,
            value=200,
            step=10
        )

    presentation_min = st.slider(
        "Présentation minimale (décoration/propreté)",
        min_value=1,
        max_value=10,
        value=6,
        step=1
    )

    description = st.text_area(
        "Vos envies de vacances",
        placeholder="Ex: Petite maison avec vue sur mer, proche plage, piscine...",
        value=""
    )

    return {
        "intention": "rs",
        "budget_max": budget,
        "surface_min": surface_min,
        "quartiers": [],
        "description_libre": f"{description} type:{type_loc} distance_max:{distance_max}km presentation_min:{presentation_min}"
    }


def formulaire_mixte():
    """Formulaire pour Immeuble Mixte avec filtres dynamiques"""
    budget = st.number_input(
        "Budget d'investissement (€)",
        min_value=500_000,
        max_value=10_000_000,
        value=1_000_000,
        step=50_000
    )

    col1, col2 = st.columns(2)
    with col1:
        nb_logements_min = st.slider(
            "Nombre de logements minimum",
            min_value=2,
            max_value=50,
            value=5
        )
    with col2:
        ratio_commercial = st.slider(
            "Ratio commercial / résidentiel (%)",
            min_value=0,
            max_value=50,
            value=20,
            step=5
        )

    rendement_min = st.slider(
        "Rendement estimé minimum (%)",
        min_value=2.0,
        max_value=10.0,
        value=5.0,
        step=0.5
    )

    localisation = st.selectbox(
        "Localisation préférée",
        ["Centre-ville Toulon", "Secteur dynamique", "Zone commerciale", "Peu importe"]
    )
    description = st.text_area(
        "Votre stratégie d'acquisition",
        placeholder="Ex: Immeuble avec rendement fort, potentiel de rénovation, baux stables...",
        value=""
    )

    return {
        "intention": "mixte",
        "budget_max": budget,
        "surface_min": 0,
        "quartiers": [localisation] if localisation != "Peu importe" else [],
        "description_libre": f"{description} logements_min:{nb_logements_min} ratio_commercial:{ratio_commercial}% rendement_min:{rendement_min}%"
    }


# ============================================================================
# MAIN
# ============================================================================
def main():
    if st.session_state.page == "accueil":
        afficher_accueil()
    elif st.session_state.page == "recherche":
        afficher_recherche()


if __name__ == "__main__":
    main()
