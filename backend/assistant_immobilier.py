"""
Assistant immobilier : comprend une question utilisateur, retrouve les annonces
pertinentes dans ChromaDB, construit un prompt conseiller et produit une analyse
via Claude.
"""
from __future__ import annotations

import os
import csv
import re
from pathlib import Path
from typing import Any

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

if load_dotenv:
    load_dotenv()

DATA_CSV = Path("data/annonces_p1.csv")

_anthropic_client: Any | None = None


def _get_anthropic_client() -> Any:
    global _anthropic_client
    if _anthropic_client is None:
        import anthropic

        _anthropic_client = anthropic.Anthropic()
    return _anthropic_client


def _to_float(value: Any) -> float | None:
    if value in ("", None):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _to_int(value: Any) -> int | None:
    number = _to_float(value)
    return int(number) if number is not None else None


def charger_annonces_csv(path: Path = DATA_CSV) -> list[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as csv_file:
        annonces = list(csv.DictReader(csv_file))
    for annonce in annonces:
        annonce["prix"] = _to_float(annonce.get("prix"))
        annonce["surface"] = _to_float(annonce.get("surface"))
        annonce["nb_pieces"] = _to_int(annonce.get("nb_pieces"))
        annonce["photos_count"] = _to_int(annonce.get("photos_count"))
    return annonces


def indexer_si_vide() -> int:
    """Remplit ChromaDB si la collection est vide, depuis Supabase en priorité."""
    from .rag import get_collection, indexer_annonces

    collection = get_collection()
    if collection.count() > 0:
        return collection.count()
    try:
        from supabase import create_client
        sb = create_client(os.getenv("SUPABASE_URL", ""), os.getenv("SUPABASE_KEY", ""))
        annonces = sb.table("annonces").select("*").execute().data
        if annonces:
            indexer_annonces(annonces)
            return get_collection().count()
    except Exception:
        pass
    annonces = charger_annonces_csv()
    indexer_annonces(annonces)
    return get_collection().count()


# Alias pour compatibilité avec les appels existants
indexer_csv_si_vide = indexer_si_vide


def comprendre_question(user_query: str) -> dict:
    """Extrait quelques criteres simples depuis la phrase utilisateur."""
    query = user_query.casefold()
    type_bien = None
    match_type = re.search(r"\bt\s*([1-6])\b", query)
    if match_type:
        type_bien = f"T{match_type.group(1)}"

    budget_max = None
    match_budget = re.search(r"(?:moins de|<|max(?:imum)?|budget)\s*(\d+(?:[.,]\d+)?)\s*k", query)
    if match_budget:
        budget_max = float(match_budget.group(1).replace(",", ".")) * 1000
    else:
        match_budget = re.search(r"(?:moins de|<|max(?:imum)?|budget)\s*(\d[\d\s]{3,})", query)
        if match_budget:
            budget_max = float(match_budget.group(1).replace(" ", ""))

    ville = "Toulon" if "toulon" in query else None
    objectif = "investissement" if any(word in query for word in ("investir", "investissement", "rentable", "locatif")) else "achat"
    return {
        "type_bien": type_bien,
        "ville": ville,
        "budget_max": budget_max,
        "objectif": objectif,
    }


def _respecte_criteres(annonce: dict, criteres: dict) -> bool:
    if criteres.get("ville") and str(annonce.get("ville", "")).casefold() != criteres["ville"].casefold():
        return False
    prix = _to_float(annonce.get("prix"))
    if criteres.get("budget_max") and prix and prix > criteres["budget_max"]:
        return False
    if criteres.get("type_bien"):
        type_query = criteres["type_bien"].casefold()
        type_annonce = str(annonce.get("type", "")).casefold()
        pieces = annonce.get("nb_pieces")
        if type_query not in type_annonce and str(pieces or "") != type_query.replace("t", ""):
            return False
    return True


def retrouver_bonnes_annonces(user_query: str, n_results: int = 5) -> list[dict]:
    from .rag import search_similar

    indexer_si_vide()
    annonces = search_similar(user_query, n_results=n_results)
    criteres = comprendre_question(user_query)
    filtrees = [annonce for annonce in annonces if _respecte_criteres(annonce, criteres)]
    return filtrees or annonces


def construire_prompt(user_query: str, biens: list[dict]) -> str:
    lignes = [
        "Tu es ToulonfindIA, un conseiller immobilier IA specialise sur le marche de Toulon.",
        "",
        "Objectif : aider l'utilisateur a choisir les annonces les plus pertinentes "
        "en expliquant les opportunites, les risques et les prochaines actions.",
        "",
        "Methode d'analyse interne :",
        "1. Identifier le besoin utilisateur : type de bien, budget, ville, quartier, objectif.",
        "2. Comparer chaque annonce aux criteres explicites de la question.",
        "3. Evaluer les opportunites : prix, surface, localisation, potentiel locatif, coherence prix/m2.",
        "4. Evaluer les risques : DPE absent, photos insuffisantes, travaux possibles, prix ou pieces manquants.",
        "5. Prioriser les biens et donner une recommandation claire.",
        "",
        "N'affiche pas ton raisonnement etape par etape. Donne seulement une reponse utile, claire et structuree.",
        "",
        "Format attendu :",
        "- Resume de la demande",
        "- Top recommandations classees",
        "- Opportunites",
        "- Risques / points a verifier",
        "- Recommandation finale",
        "",
        "Voici les biens retrouves par le RAG :",
    ]
    for index, bien in enumerate(biens, start=1):
        lignes.append(
            "- Bien {idx}: {type_bien}, {surface} m2, {ville}, {quartier}, "
            "{prix} EUR, {pieces} pieces. Description: {description}. URL: {url}".format(
                idx=index,
                type_bien=bien.get("type") or "bien",
                surface=bien.get("surface") or "surface inconnue",
                ville=bien.get("ville") or "ville inconnue",
                quartier=bien.get("quartier") or "quartier inconnu",
                prix=bien.get("prix") or "prix inconnu",
                pieces=bien.get("nb_pieces") or "nombre inconnu",
                description=(bien.get("description") or bien.get("document") or "")[:220],
                url=bien.get("url_source") or "",
            )
        )
    lignes.extend([
        "",
        f"Question : {user_query}",
        "",
        "Reponds en francais. Sois concret, factuel, et cite les biens par numero.",
        "Si une information manque, signale-la comme point a verifier au lieu de l'inventer.",
    ])
    return "\n".join(lignes)


def _prix_m2(bien: dict) -> float | None:
    prix = _to_float(bien.get("prix"))
    surface = _to_float(bien.get("surface"))
    if not prix or not surface:
        return None
    return prix / surface


def repondre_avec_analyse(user_query: str, biens: list[dict]) -> str:
    """Réponse de secours basée sur des règles, si Claude n'est pas disponible."""
    criteres = comprendre_question(user_query)
    if not biens:
        return (
            "Je n'ai pas trouve d'annonce assez proche dans la base. "
            "Essayez une recherche plus large, par exemple : T3 Toulon investissement."
        )

    lignes = ["Voici les biens les plus pertinents pour votre recherche."]
    for index, bien in enumerate(biens, start=1):
        prix_m2 = _prix_m2(bien)
        opportunites = []
        risques = []

        if criteres.get("budget_max") and bien.get("prix") and bien["prix"] <= criteres["budget_max"]:
            opportunites.append("prix compatible avec le budget")
        if criteres.get("objectif") == "investissement":
            opportunites.append("potentiel locatif a verifier selon le quartier et les charges")
        if prix_m2:
            opportunites.append(f"prix au m2 estime a {prix_m2:,.0f} EUR/m2")
        if not bien.get("dpe"):
            risques.append("DPE non renseigne")
        if not bien.get("photos_count"):
            risques.append("peu ou pas de photos")
        if bien.get("prix") is None:
            risques.append("prix manquant")

        lignes.append("")
        lignes.append(f"Proposition {index} - {bien.get('type') or 'Bien'} a {bien.get('quartier') or bien.get('ville')}")
        lignes.append(f"Prix: {bien.get('prix') or 'non renseigne'} EUR | Surface: {bien.get('surface') or 'non renseignee'} m2 | Pieces: {bien.get('nb_pieces') or 'non renseigne'}")
        lignes.append("Opportunites: " + "; ".join(opportunites or ["annonce pertinente par rapport a la question"]))
        lignes.append("Risques: " + "; ".join(risques or ["a verifier: charges, DPE, travaux, copropriete"]))
        lignes.append("Recommandation: comparer le prix au m2 avec le quartier, demander les charges et verifier la rentabilite nette.")
        if bien.get("url_source"):
            lignes.append(f"URL: {bien['url_source']}")

    lignes.append("")
    lignes.append("Synthese: privilegiez les biens qui respectent le budget, ont un DPE clair, assez de photos et un prix au m2 coherent pour Toulon.")
    return "\n".join(lignes)


def _generer_reponse_llm(prompt: str, user_query: str, biens: list[dict]) -> str:
    """Appelle Claude pour générer une réponse, avec fallback sur l'analyse locale."""
    try:
        response = _get_anthropic_client().messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text
    except Exception:
        return repondre_avec_analyse(user_query, biens)


def assistant_immobilier(user_query: str, n_results: int = 5) -> dict:
    biens = retrouver_bonnes_annonces(user_query, n_results=n_results)
    prompt = construire_prompt(user_query, biens)
    reponse = _generer_reponse_llm(prompt, user_query, biens)
    return {
        "query": user_query,
        "criteres": comprendre_question(user_query),
        "prompt": prompt,
        "biens": biens,
        "reponse": reponse,
    }


def main() -> None:
    from argparse import ArgumentParser
    parser = ArgumentParser(description="Assistant immobilier ChromaDB")
    parser.add_argument("query", help="Question utilisateur")
    parser.add_argument("--n-results", type=int, default=5)
    args = parser.parse_args()

    resultat = assistant_immobilier(args.query, n_results=args.n_results)
    print(resultat["reponse"])


if __name__ == "__main__":
    main()
