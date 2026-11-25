# KPI : Prix médian d’une vente

## Définition
Montant en euros d’une vente typique dans le département : la moitié des ventes sont conclues en dessous, l’autre moitié au-dessus.

## Calcul
Médiane de la valeur foncière des ventes de logements par département (et surface médiane associée). Table gold : `gold_departement.prix_median` et `surface_mediane`.

## Intérêt pour le persona (Claire, directrice du développement d’un réseau d’agences)
Complète le prix au m² : c’est le **montant réel** d’une transaction, utile pour estimer le chiffre d’affaires d’une agence à partir d’une vente moyenne.

## Lecture et limites
Un prix médian élevé peut venir de grandes surfaces autant que de prix élevés : la surface médiane est affichée à côté.
