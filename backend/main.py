from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, BackgroundTasks
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pydantic import BaseModel
from .ingestion import sync

scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.add_job(sync, "cron", hour=7, minute=0)
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(title="NidBuyer API", version="0.1.0", lifespan=lifespan)


class ProfilAcheteur(BaseModel):
    intention: str
    budget_max: float
    surface_min: float | None = None
    quartiers: list[str] = []
    nb_pieces_min: int | None = None
    description_libre: str = ""


class AlerteProfil(BaseModel):
    email: str
    profil: ProfilAcheteur


@app.get("/biens")
def liste_biens(budget_max: float | None = None, surface_min: float | None = None, quartier: str | None = None):
    raise HTTPException(status_code=501, detail="Non implémenté")


@app.get("/biens/{bien_id}")
def detail_bien(bien_id: str):
    raise HTTPException(status_code=501, detail="Non implémenté")


@app.post("/rechercher")
def rechercher(profil: ProfilAcheteur):
<<<<<<< Updated upstream
    """Profil acheteur → top 5 biens avec scores et fiches décision."""
=======
    """Profil acheteur → top 5 biens avec scores, fiches décision enrichies."""
>>>>>>> Stashed changes
    from .rag import search_similar
    from .scoring import score_opportunite, fiche_decision, rendement_locatif

    query = f"{profil.description_libre} {profil.intention}"
<<<<<<< Updated upstream
    filtre = {"quartier": {"$in": profil.quartiers}} if profil.quartiers else None

    mediane_dvf = {"rp": 4500, "rs": 4200, "investissement": 4300, "mixte": 4400}.get(profil.intention, 4500)
    dvf_dict = {"mediane_prix_m2": mediane_dvf}

    biens = search_similar(query, n=20, filtre_meta=filtre)

    resultats = []
    for bien in biens:
        try:
            prix = float(bien.get("prix") or 0)
            surface = float(bien.get("surface") or 0)
        except (ValueError, TypeError):
            continue

        if prix > profil.budget_max:
            continue
        if profil.surface_min and surface < profil.surface_min:
            continue

        bien_num = {**bien, "prix": prix, "surface": surface}
        scoring = score_opportunite(bien_num, dvf_dict)
        fiche = fiche_decision(bien_num, profil.intention)

        resultat = {
            "id": bien.get("id"),
            "titre": bien.get("titre") or f"{bien.get('type', '')} {bien.get('quartier', '')}".strip(),
            "prix": prix,
            "surface": surface,
            "quartier": bien.get("quartier"),
            "pieces": bien.get("nb_pieces") or bien.get("pieces"),
            "type": bien.get("type"),
            "description": bien.get("description"),
            "url": bien.get("url_source") or bien.get("url"),
            "image_url": bien.get("image_url"),
            "scoring": scoring,
            "fiche": fiche,
        }

        if profil.intention == "investissement":
            loyer_estime = prix * 0.005
            resultat["rendement"] = rendement_locatif(bien_num, loyer_estime / 12)
=======
    filtre = {}
    if profil.quartiers:
        filtre = {"quartier": {"$in": profil.quartiers}}

    biens = search_similar(query, n_results=5, filtre_meta=filtre)

    mediane_dvf = {
        "rp": 4500,
        "rs": 4200,
        "investissement": 4300,
        "mixte": 4400
    }.get(profil.intention, 4500)

    resultats = []
    for bien in biens:
        if bien.get("prix", 0) > profil.budget_max:
            continue
        if profil.surface_min and bien.get("surface", 0) < profil.surface_min:
            continue

        scoring = score_opportunite(bien, mediane_dvf, profil.intention)
        fiche = fiche_decision(bien, {"mediane": mediane_dvf}, profil.intention)

        resultat = {
            "id": bien.get("id"),
            "titre": fiche["titre"],
            "prix": fiche["prix"],
            "surface": fiche["surface"],
            "quartier": fiche["quartier"],
            "pieces": fiche["pieces"],
            "type": fiche["type"],
            "description": bien.get("description"),
            "url": bien.get("url"),
            "scoring": scoring,
            "fiche_enrichie": fiche,
        }

        if profil.intention == "investissement":
            loyer_estime = bien.get("prix", 0) * 0.005
            resultat["rendement"] = rendement_locatif(bien, loyer_estime / 12)
>>>>>>> Stashed changes

        resultats.append(resultat)

    return {
        "profil": {
            "intention": profil.intention,
            "budget_max": profil.budget_max,
            "surface_min": profil.surface_min,
        },
        "resultats": resultats[:5],
<<<<<<< Updated upstream
        "nb_resultats": len(resultats),
=======
        "nb_resultats": len(resultats)
>>>>>>> Stashed changes
    }


@app.post("/chat")
def chat(question: str, profil: ProfilAcheteur | None = None):
    raise HTTPException(status_code=501, detail="Non implémenté")


@app.post("/alerte")
def creer_alerte(alerte: AlerteProfil):
    raise HTTPException(status_code=501, detail="Non implémenté")


@app.get("/marche/quartiers")
def marche_quartiers():
    raise HTTPException(status_code=501, detail="Non implémenté")


@app.post("/admin/sync")
def admin_sync(background_tasks: BackgroundTasks, dry_run: bool = False):
    background_tasks.add_task(sync, dry_run=dry_run)
    return {"status": "sync lancée en arrière-plan", "dry_run": dry_run}


@app.get("/admin/status")
def admin_status():
    from pathlib import Path
    from .rag import get_collection
    try:
        n = get_collection().count()
    except Exception:
        n = 0
    last_sync = Path("data/.last_sync")
    return {
        "annonces_indexees": n,
        "derniere_sync": last_sync.read_text() if last_sync.exists() else "jamais",
    }
