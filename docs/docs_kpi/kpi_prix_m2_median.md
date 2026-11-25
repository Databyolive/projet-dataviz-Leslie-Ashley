# KPI : Prix au m² médian

## Définition
Prix de vente au mètre carré habitable : la moitié des ventes du département se font en dessous de cette valeur, l’autre moitié au-dessus.

## Calcul
Pour chaque vente : valeur foncière ÷ surface bâtie du logement. On prend la **médiane** (exacte, `F.median` dans Spark) par département. Table gold : `gold_departement.prix_m2_median`.

## Intérêt pour le persona (Claire, directrice du développement d’un réseau d’agences)
Donne le **niveau de prix** du marché indépendamment de la taille des biens. C’est la base de la comparaison entre départements.

## Lecture et limites
La médiane résiste aux ventes extrêmes. Les ventes de moins de 500 € ou plus de 30 000 € par m² ont été écartées lors du nettoyage.
