# Journal des expérimentations — Prompt Engineering

Comparez **3 versions** du system prompt sur le **même bien de référence**.

---

## Bien de référence (à choisir une fois, garder pour toutes les versions)

> ** Notre bien : Charmante maison 4 pièces 82m2 sur terrain 500m2 / Située à Toulon (quartier L’Escaillon)
Prix : 426 000 € / Bénéficie d'un extérieur 

---

## V1 — Prompt basique

```
Tu es un conseiller immobilier expert.

Analyse cette annonce :

Maison 4 pièces de 82 m²
Située à Toulon (quartier L’Escaillon)
Prix : 426 000 €
Bénéficie d'un extérieur 
 
Est-ce une bonne opportunité d’achat ?
```

**Réponse obtenue sur le bien de référence :**

> Analyse rapide du bien à Toulon (L’Escaillon)
Prix au m²
426 000 € / 82 m² ≈ 5 195 €/m²

À comparer :

Moyenne Toulon : ~3 500 à 4 500 €/m² (variable selon quartiers)
Quartiers très recherchés (Cap Brun, Mourillon) : plus élevés
L’Escaillon : quartier plutôt populaire / intermédiaire

Conclusion prix : probablement au-dessus du marché local


Points positifs :

Toulon = ville dynamique (mer, emploi, base militaire, location)
Bonne demande locative globale

Points de vigilance :

L’Escaillon = moins recherché que d’autres secteurs
Image du quartier pouvant impacter revente et valorisation

Le bien : 
Atouts :

Maison (plus rare et recherchée qu’un appartement)
Surface correcte (82 m²)
Bénéficie d'un extérieur 

Risques :

Surévaluation du prix
Revente potentiellement difficile
Rentabilité locative faible si investissement
Mauvaise surprise si travaux importants

Verdict :

Plutôt une opportunité moyenne à faible en l’état
Peut devenir intéressante si :
Négociation significative (important ici)

Sinon :
Prix probablement trop élevé pour le secteur

**Analyse :**

- Ce qui fonctionne :
Calcul automatique du prix/m²
Mise en contexte géographique

- Ce qui manque :
Pas de donnée précise du quartier
Pas de hiérarchisation des risques
Absence de recommandation ferme
Manque de sources
---

## V2 — Format de sortie structuré

```
Tu es un expert en immobilier.

Analyse cette annonce :

Maison 4 pièces de 82 m²
Située à Toulon (quartier L’Escaillon)
Prix : 426 000 €
Bénéficie d'un extérieur 

Réponds en respectant cette structure :

## Opportunités
- 

## Risques
- 

## Analyse du prix
- 

## Conseils
- 

## Verdict
- Achat recommandé / Prudent / Déconseillé / À éviter + justification 
```

**Réponse obtenue sur le bien de référence :**

> Analyse – Maison à Toulon (L’Escaillon)

Opportunités :

Bien de type maison, plus rare et généralement plus recherché que les appartements
Surface de 82 m², avec 4 pièces, adaptée pour une résidence principale
Marché immobilier actif à Toulon (demande soutenue, notamment en résidence principale)
Potentiel de valorisation, le bien dispose d’atouts (extérieur, stationnement, jacuzzi)


Risques :

Quartier L’Escaillon moins recherché que d’autres secteurs → impact sur la revente
Prix élevé pour le secteur sans garantie de prestations supérieures
Risque de faible rentabilité locative à ce niveau de prix


Analyse du prix :

Prix au m² ≈ 5 195 €/m²
Moyenne à Toulon : environ 3 500 à 4 500 €/m² selon les quartiers
L’Escaillon se situe généralement en dessous des secteurs premium


Conclusion : bien probablement surévalué, sauf caractéristiques haut de gamme non mentionnées

Conseils 

Vérifier en priorité :
Etat du bien et éventuels travaux qui seraient à réaliser (engagement de sommes supplémentaires) 

Comparer avec des biens similaires dans le même secteur

Envisager une négociation significative (-5 à -10 %)

Éviter toute décision rapide sans validation du prix de marché


Verdict :

Prudent
Ce n’est pas une mauvaise opportunité, mais le prix semble élevé pour le secteur.
L’achat peut être pertinent uniquement si :

le bien offre des prestations supérieures justifiant le prix
ou une négociation permet de le repositionner au niveau du marché

Sinon, le risque principal est de surpayer avec une revente plus difficile.

**Analyse :**

- Ce qui s'est amélioré :
Prompt structuré
Consigne plus ferme sur le verdict
Liste mieux structurée
Négociation chiffrée
Synthèse plus claire

- Ce qui reste perfectible :
Toujours pas de donnée précise du quartier
Le verdict manque toujours de clarté
Manque de sources 
---

## V3 — Chain-of-thought

```
Tu es un expert en investissement immobilier dans le département du Var (sud de la France)

Analyse en profondeur cette annonce :

Maison 4 pièces de 82 m²
Située à Toulon (quartier L’Escaillon)
Prix : 426 000 €
Bénéficie d'un extérieur 

Procède étape par étape :
1. Estime le prix au m² et compare-le au marché local de Toulon
2. Analyse l’attractivité du quartier (résidentiel, demande locative, accessibilité)
3. Évalue le potentiel du bien (revente, location, valorisation)
4. Identifie les risques (prix élevé, travaux potentiels, environnement) 
5. Estime si le prix est cohérent ou surévalué

Ensuite, fournis uniquement : 

## Opportunités
- 

## Risques
- 

## Analyse du prix
- (€/m² + positionnement marché)

## Recommandation
- Acheter / Négocier / Éviter + justification claire et argumentée, s'appuyant sur des faits. 

Est-ce une bonne opportunité d’achat ?
```

**Réponse obtenue sur le bien de référence :**

> Analyse – Maison à Toulon (L’Escaillon)
> 
Opportunités :

Maison individuelle (produit recherché, plus rare que les appartements)
Surface de 82 m², avec 4 pièces, adaptée à une résidence principale familiale
Marché immobilier toulonnais dynamique avec une demande soutenue (+ progression sur plusieurs années)
Potentiel de valorisation, le bien dispose d’atouts (extérieur, stationnement, jacuzzi)

Risques :

Quartier L’Escaillon moins valorisé que les secteurs premium → impact sur revente
Prix très supérieur aux standards locaux → risque de surpayer
Rentabilité locative faible à ce niveau d’achat
Marché local du quartier en légère baisse récente (signal de prudence)

Analyse du prix :

Prix du bien : 426 000 € / 82 m² = ~5 195 €/m²

Comparaison :

Moyenne maisons à Toulon : ~4 000 à 4 700 €/m²
Quartier L’Escaillon :
~3 000 €/m² médian
~3 600 €/m² pour maisons

Écart : +40 % à +70 % au-dessus du marché local

Conclusion : prix fortement surévalué, sauf bien exceptionnel (ce qui n’est pas indiqué)

Recommandation :

Négocier fortement voire éviter

Ce bien n’est pas une bonne opportunité en l’état :

Le prix est objectivement déconnecté du marché du quartier
L’Escaillon n’est pas un secteur justifiant un premium élevé
Le risque principal est une moins-value à la revente

À considérer uniquement si :

prestations haut de gamme (rare dans ce secteur)
ou négociation importante (-15 % à -25 %) pour se rapprocher du marché

Sinon :

investissement risqué
mauvaise optimisation du capital

Conclusion rapide :

Non, ce n’est pas une bonne opportunité d’achat aujourd’hui, sauf cas très spécifique ou forte négociation.

**Analyse :**

- Pourquoi V3 > V1 ?
Précision des données chiffrées :
V1 --> Comparaison vague / V3 --> Écart calculé : +40% à +70%
Qualité de la recommandation :
V1 --> « Plutôt une opportunité moyenne à faible » / V3 --> « Non, pas une bonne opportunité d'achat »
Prise en compte du contexte dans sa globalité :
V1 --> Analyse restrictive (juste le bien vs marché moyen) / V3 --> Mention explicite (en temps réel): « Marché local du quartier en légère baisse récente »

- Trade-off (longueur, coût tokens, latence) :
Longueur de réponse : 450 mots (environ 50% de plus que la V1)
Tokens en entrée : 200 (prompt + instructions) contre 50 pour la V1
Tokens en sortie : 600 contre 400 pour la V1
Latence : Moyenne vs Faible pour la V1

---

## Conclusion

Version retenue en production : **V?**

Raison principale :
