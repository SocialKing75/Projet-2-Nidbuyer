# R&D Vision — Choix d'approche et résultats

## Approche retenue

**CNN / LLM multimodal / Autre** *(barrer les mentions inutiles)*

Modèle : __LLM multimodal : LLAVA__

Justification du choix :
- Pourquoi cette approche plutôt que l'alternative ?
  
Polyvalence : Contrairement à un CNN classique, le LLM multimodal permet d'extraire simultanément plusieurs dimensions complexes comme le type de pièce ou l'état général du bien, le tout via un seul "prompt". 

Performance : Avec un taux de succès de 53.3% sur des données brutes sans entraînement, le modèle montre une bonne capacité de compréhension, supérieure aux approches classiques.

- Contraintes prises en compte (données disponibles, coût, temps) :
  
Latence vs Précision : Nous avons fait le choix d'accepter une attente d'environ 4,5 secondes par analyse. Délai justifié par la précision des résultats : nous préférons un temps de réponse légèrement plus long pour obtenir une analyse plus détaillée plutôt qu'un résultat instantané mais superficiel."

Temps : L'approche LLM a permis un déploiement rapide (gain de temps majeur pour le projet). 

---

## Dataset

| | Valeur |
|--|--|
| Nombre de photos labellisées | "aucun label nécessaire" 30 photos testées |
| Source des photos | Bienici : https://www.bienici.com/ |
| Répartition par classe | excellent: X / bon: X / correct: X / à rénover: X |

*(Si LLM : indiquer "aucun label nécessaire" et le nombre de photos testées)*

---

## Résultats

### Métriques sur jeu de test

| Classe | Précision | Rappel | F1 |
|--------|-----------|--------|----|
| excellent | | | |
| bon | | | |
| correct | | | |
| a_renover | | | |

**Accuracy globale :** 53,3%

### Exemples de prédictions

| Photo | Vérité terrain | Prédiction | Correct ? |
|-------|---------------|------------|-----------|
| photo_001.jpg | a_renover | a_renover | ✓ |
| photo_002.jpg | bon | correct | ✗ |

---

## Coût

*(Si LLM uniquement)*

| Modèle testé | Coût / photo | Coût total tests | Qualité estimée |
| LLAVA|-------------|"0-5k": 8, "5-20k": 4,"20-50k": 4
------|----------------|
| | | | |

---

## Limites et biais

- Ce que le modèle rate systématiquement :
- Conditions où il se trompe :
- Ce qu'on ferait différemment avec plus de temps :

---

## Intégration dans le scoring

La fonction `vision.model.evaluer_etat_bien()` est appelée dans `backend/scoring.py`
via le paramètre `vision_result`. Impact sur le score d'opportunité :

- Profil investisseur : travaux = opportunité → malus = 0
- Profil RP famille : travaux = frein → malus = 0.3
