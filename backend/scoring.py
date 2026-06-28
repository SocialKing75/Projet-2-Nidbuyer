"""Calcul du score d'opportunité d'un bien immobilier."""

MALUS_TRAVAUX = {
    "investissement": 0.0,
    "rp": 0.3,
    "rs": 0.15,
    "mixte": 0.1,
}


def score_opportunite(bien: dict, mediane_quartier: float, profil: str, vision_result: dict = None) -> dict:
    """Calcule le score d'opportunité d'un bien."""
    prix = bien.get("prix", 0)
    surface = bien.get("surface", 1)
    prix_m2 = prix / surface if surface > 0 else 0

    ecart_pct = ((prix_m2 - mediane_quartier) / mediane_quartier * 100) if mediane_quartier > 0 else 0

    malus = MALUS_TRAVAUX.get(profil, 0.0)
    if vision_result and vision_result.get("travaux_detectes"):
        ecart_pct += malus * 100

    score = max(0, min(100, 50 + (20 - abs(ecart_pct) / 5)))

    if score >= 75:
        label = "Très bon"
    elif score >= 60:
        label = "Bon"
    elif score >= 40:
        label = "Moyen"
    else:
        label = "À éviter"

    return {
        "score": round(score, 1),
        "ecart_pct": round(ecart_pct, 1),
        "label": label,
        "prix_m2": round(prix_m2, 0)
    }


def fiche_decision(bien: dict, dvf_quartier: dict, profil: str = "rp") -> dict:
    """Génère une fiche complète avec analyse spécifique au profil."""
    prix = bien.get("prix", 0)
    surface = bien.get("surface", 1)
    quartier = bien.get("quartier", "")
    pieces = bien.get("pieces", 0)
    bien_type = bien.get("type", "")

    mediane = dvf_quartier.get("mediane", 4500)
    scoring = score_opportunite(bien, mediane, profil)

    opportunites = _analyser_opportunites(bien, scoring, profil)
    risques = _analyser_risques(bien, scoring, profil)
    conseil = _generer_conseil(bien, scoring, profil)

    return {
        "titre": bien.get("titre", ""),
        "prix": prix,
        "surface": surface,
        "pieces": pieces,
        "type": bien_type,
        "quartier": quartier,
        "prix_m2": scoring["prix_m2"],
        "ecart_pct": scoring["ecart_pct"],
        "score": scoring["score"],
        "label": scoring["label"],
        "opportunites": opportunites,
        "risques": risques,
        "conseil": conseil,
    }


def _analyser_opportunites(bien: dict, scoring: dict, profil: str) -> list:
    opps = []
    if scoring["ecart_pct"] < -10:
        opps.append("Prix très intéressant - bien sous-évalué")
    if profil == "rp":
        if bien.get("pieces", 0) >= 3:
            opps.append("Suffisant pour une famille")
        if bien.get("surface", 0) >= 80:
            opps.append("Bonne surface habitable")
    elif profil == "investissement":
        loyer_estime = bien.get("prix", 0) * 0.005 / 12
        if loyer_estime > 0:
            rendement = (loyer_estime * 12) / bien.get("prix", 1) * 100
            if rendement >= 4:
                opps.append(f"Rendement estimé intéressant ({rendement:.1f}%)")
    elif profil == "rs":
        if scoring["ecart_pct"] < 0:
            opps.append("Investissement secondaire à bon prix")
    elif profil == "mixte":
        if bien.get("type") == "Immeuble":
            opps.append("Type idéal pour rendement mixte")
    return opps if opps else ["Bien équilibré"]


def _analyser_risques(bien: dict, scoring: dict, profil: str) -> list:
    risques = []
    if scoring["ecart_pct"] > 15:
        risques.append("Prix élevé par rapport à la région")
    if profil == "rp":
        if bien.get("surface", 0) < 50:
            risques.append("Surface réduite pour résidence principale")
        if bien.get("pieces", 0) < 2:
            risques.append("Trop petit pour famille")
    elif profil == "investissement":
        if bien.get("type") == "Studio":
            risques.append("Studio: marché saturé, vacance possible")
    elif profil == "rs":
        if scoring["score"] < 40:
            risques.append("État général médiocre pour lieu de vacances")
    elif profil == "mixte":
        if bien.get("type") != "Immeuble":
            risques.append("Type non optimal pour usage mixte")
    return risques if risques else ["Peu de risques identifiés"]


def _generer_conseil(bien: dict, scoring: dict, profil: str) -> str:
    if profil == "rp":
        if scoring["score"] >= 75:
            return "Bien aligné pour résidence principale. À visiter en priorité."
        elif scoring["score"] >= 60:
            return "Bon compromis prix/qualité. À considérer sérieusement."
        else:
            return "À comparer avec d'autres options avant de décider."
    elif profil == "investissement":
        if scoring["score"] >= 75:
            return "Excellent potentiel d'investissement. Vérifier rendement réel."
        elif scoring["score"] >= 60:
            return "Investissement viable. Négocier le prix."
        else:
            return "Rendement insuffisant. Continuer la recherche."
    elif profil == "rs":
        if scoring["score"] >= 75:
            return "Idéal pour résidence secondaire. Prix avantageux."
        elif scoring["score"] >= 60:
            return "Bon compromis pour vacances. À visiter."
        else:
            return "À éviter pour résidence secondaire."
    elif profil == "mixte":
        if scoring["score"] >= 75:
            return "Très bon pour usage mixte. Analyser mix résidentiel/commercial."
        elif scoring["score"] >= 60:
            return "Potentiel pour mixte. À étudier davantage."
        else:
            return "Non recommandé pour usage mixte."
    return "À étudier."


def rendement_locatif(bien: dict, loyer_estime: float) -> dict:
    """Calcule le rendement brut et net estimé."""
    prix = bien.get("prix", 1)
    loyer_annuel = loyer_estime * 12
    rendement_brut = (loyer_annuel / prix * 100) if prix > 0 else 0
    rendement_net = rendement_brut * 0.75
    return {
        "rendement_brut_pct": round(rendement_brut, 2),
        "rendement_net_pct": round(rendement_net, 2),
        "loyer_mensuel_estime": round(loyer_estime, 0)
    }