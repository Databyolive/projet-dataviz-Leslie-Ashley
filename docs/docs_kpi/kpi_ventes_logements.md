# KPI : Ventes de logements

## Définition
Nombre de ventes de logements (maisons et appartements) enregistrées dans le département en 2025, après nettoyage des données.

## Calcul
Comptage des ventes de la table silver `ventes_dvf_2025` (une ligne par vente), regroupées par département et type de bien. Table gold : `gold_departement.nb_ventes`.

## Intérêt pour le persona (Claire, directrice du développement d’un réseau d’agences)
Mesure l’**activité** du marché. Pour Claire, un département où l’on vend beaucoup est un département où une agence a du travail et peut atteindre rapidement un volume d’affaires.

## Lecture et limites
Un grand département compte mécaniquement plus de ventes : à lire avec le prix et l’écart à la médiane. Seuil de fiabilité : un département sous le seuil est signalé.
