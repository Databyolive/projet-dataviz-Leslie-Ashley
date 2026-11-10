# Couche silver : règles de nettoyage

Notebooks : `notebooks/01b_exploration_bronze.ipynb` (exploration) et `notebooks/02_silver.ipynb` (règles)

NB: les chiffres fournis correspondent aux valeurs du dataset à la periode où on  a telecharger ceci dit les chiffres peuvent ne pas correspondrent car ce sont des données mis en à jour constament .


## 1. Périmètre et méthode

- **Source** : DVF géolocalisées, année 2025.
- **Entrée** : 3 793 113 lignes, soit **1 384 341 mutations** (une mutation = une vente, qui occupe une ou plusieurs lignes).
- **Objectif** : obtenir **une ligne par vente de logement**, avec un prix au m² fiable, pour répondre à la question de Claire.
- **Colonnes conservées** : 14 sur 40, celles nécessaires à la question du persona  plus `nature_mutation` (règle R1) et `lot1_numero` (pour distinguer les logements). Elles sont sélectionnées dès le début.
- **Comptage** : chaque règle est comptée en **lignes** et en **mutations**, car une règle retire des ventes entières. Les chiffres viennent du journal du notebook (fonction `appliquer`), pas de saisies manuelles.
- **Ordre des règles** : il compte. Le nombre retiré par une règle dépend de celles qui la précèdent.
- **Principe** : chaque règle repose sur une observation des données (notebook d'exploration), pas sur une supposition.

## 2. Typage

La bronze est entièrement en texte. La conversion utilise `try_cast`, qui renvoie `NULL` pour une valeur non convertible .

| Colonne | Type silver |
|---|---|
| `date_mutation` | date |
| `valeur_fonciere` | double |
| `surface_reelle_bati` | double |
| `nombre_pieces_principales` | entier |
| `longitude`, `latitude` | double |
| `code_departement`, `code_commune`, `id_parcelle` | **texte** (conservés tels quels : un code comme `01` perdrait son zéro) |




**Résultat : 804 803 ventes retenues, soit **58,1 %** des mutations et **52,4 %** des lignes de départ. La table silver compte 804 803 lignes (une par vente) ; 

## 3. Détail des règles

### R1 : seulement les ventes
- **Définition** : `nature_mutation = 'Vente'` .
- **Observation** (valeurs de `nature_mutation`) :

| Nature | Mutations | Lignes |
|---|---|---|
| **Vente** | 1 309 960 | 3 585 313 |
| Vente en l'état futur d'achèvement (VEFA) | 51 982 | 143 873 |
| Échange | 13 277 | 45 710 |
| Vente terrain à bâtir | 4 653 | 8 116 |
| Adjudication | 2 665 | 8 060 |
| Expropriation | 1 817 | 2 041 |

- **Justification** : les échanges, adjudications et expropriations ne correspondent pas à un prix de marché librement fixé ; le terrain à bâtir n'a pas de logement.
- **Cas de la VEFA** (70 % de ce que R1 retire), Pourquoi?:
   43 915 des 51 982 mutations VEFA (84,5 %) n'ont aucun logement déclaré (aucun local : 41 318 ; dépendance ou local commercial seulement : 2 597) et auraient été retirées par R4a de toute façon ;
  
- **Effet** : 74 381 mutations retirées.

### R2 : prix renseigné
- **Définition** : `valeur_fonciere > 0`.
- **Observation** : 50 484 lignes de la bronze n'ont pas de prix (vide ou non convertible) ; **aucun prix n'est nul ni négatif**. La règle n'écarte donc que des prix vides.
- **Justification** : sans prix, aucun calcul de prix au m².
- **Effet** : 47 002 mutations retirées, qui n'occupaient chacune qu'une seule ligne (47 002 lignes).

### R3 : pas d'autre local qu'une maison, un appartement ou une dépendance
- **Définition** : aucune ligne de la mutation n'a un `type_local` non vide autre que `Maison`, `Appartement`, `Dépendance`.
- **Observation** (`type_local`) : vide (terrain) 544 751 mutations ; Dépendance 578 766 ; Maison 498 989 ; Appartement 414 292 ; **Local industriel. commercial ou assimilé** 76 149. Ce dernier est le seul « autre » type.
- **Justification** : le prix d'une vente qui comprend un local commercial ou industriel ne reflète pas un logement. Les dépendances (garage, cave) et les terrains sont tolérés : ils accompagnent normalement une maison.
- **Effet** : 72 332 mutations retirées.

### R4a : au moins un logement
- **Définition** : au moins une ligne de la mutation est une maison ou un appartement.
- **Observation** : dans la bronze, 474 361 mutations n'ont aucun logement.
- **Justification** : sans logement (terrains, bois, dépendances seules), il n'y a ni surface bâtie ni prix au m² de logement.
- **Effet** : **325 138 mutations retirées**, la règle qui pèse le plus : plus du quart des mutations restantes sont des terrains ou des dépendances.

### R4b : un seul logement distinct
- **Définition** : le nombre de logements **distincts** de la mutation vaut 1. Un logement est identifié par sa parcelle, son type, sa surface, son nombre de pièces et son numéro de lot.
- **Justification** : le prix est unique pour toute la mutation. Avec plusieurs logements, on ne sait pas le répartir, et le prix au m² serait faux.
- **Effet** : 40 679 mutations retirées.

### R5 : surface bâtie d'au moins 9 m²
- **Définition** : surface du logement ≥ 9 m².
- **Justification**  :
  - sous 5 m², les prix au m² médians sont aberrants (140 000 €/m² pour les appartements, 53 000 pour les maisons) ;
  - de 5 à 9 m², les maisons ont en moyenne 0,5 pièce : probablement des dépendances mal typées ;
  - à partir de 9 m², les prix au m² médians sont plausibles ;
  - des biens de 1 à 4 m² vendus 1 250 à 6 000 € (caves, parkings) ont un prix au m² « normal » : R6 ne les attrape pas, d'où R5.

- **Effet** : 402 mutations retirées .


### R6 : prix au m² entre 500 et 30 000 €
- **Définition** : `prix_m2 = valeur_fonciere / surface_logement`, conservé s'il est compris entre 500 et 30 000 €/m².
- **Justification**  :
  - en bas : prix symboliques (une maison de 310 m² vendue 1 €) et cessions probablement partielles ;
  - en haut : surfaces mal renseignées (un « appartement » de 1 m² vendu 800 000 €).

- **Effet** : 19 604 mutations retirées .


## 4. Table produite : `silver/ventes_dvf_2025`

Une ligne par vente (**804 803 lignes**), obtenue en gardant la ligne du logement de chaque mutation retenue.

| Colonne | Contenu |
|---|---|
| `id_mutation` | identifiant de la vente |
| `date_mutation`, `annee`, `mois` | date et sa décomposition |
| `valeur_fonciere` | prix en euros |
| `type_local` | `Maison` ou `Appartement` |
| `surface_bati`, `nb_pieces` | surface bâtie et pièces du logement |
| `code_departement`, `code_commune`, `nom_commune` | localisation (codes en texte) |
| `id_parcelle`, `longitude`, `latitude` | parcelle et coordonnées |
| `prix_m2` | prix au m² |

