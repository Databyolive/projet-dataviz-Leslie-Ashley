# Projet Data Viz — Où ouvrir la prochaine agence ? (DVF 2022)

Mastère Big Data & IA M1 — Sup de Vinci — Session 2026-2027
Enseignant : M. L. Ndao
Auteurs : Leslie AKONO, Ashley <NOM>

> Du data lake au tableau de bord : un tableau de bord  construit sur les
> transactions immobilières françaises de 2022, avec une chaîne bronze / silver / gold,
> une ontologie et des requêtes SPARQL.

## 1. Jeu de données

**Demandes de valeurs foncières géolocalisées (DVF)**, publiées par Etalab à partir des
données de la DGFiP. Elles recensent les mutations (ventes) immobilières en France,
hors Alsace-Moselle et Mayotte. Ce sont des prix réellement signés chez le notaire,
pas des prix d'annonce.

| | |
|---|---|
| Source | https://www.data.gouv.fr/datasets/demandes-de-valeurs-foncieres-geolocalisees |
| Licence | Licence Ouverte / Open Licence 2.0 |
| Fichier utilisé | `full-2022.csv.gz` (134,7 Mo compressé), livraison du 20/10/2026 |
| Période | année 2022 |
| Volume | 4 676 488 lignes dans le fichier de la livraison précédente (19/10/2026). **À recompter avec le fichier téléchargé pour prendre en compte les eventuelles mises à jour  |
| Dimension temporelle | `date_mutation` |
| Dimension géographique | commune, département, latitude / longitude |
| Téléchargement | par script, sans compte ni clé (`scripts/download_dvf.py`, à venir) |

Les données ne sont pas versionnées : le dossier `data/` est ignoré par Git.

**Remarque sur les mises à jour.** Chaque livraison semestrielle retraite l'ensemble
de l'historique. Le nombre de lignes, les coordonnées et même certains noms de colonnes
peuvent donc différer d'une livraison à l'autre, et `id_mutation` n'est pas stable
entre deux livraisons. Les chiffres de ce dépôt sont ceux de la livraison indiquée
ci-dessus.

### 1.1 Comment lire le fichier

Une **ligne** correspond à un élément vendu (une parcelle, ou un local sur une
parcelle), pas à une vente entière. Une **mutation** (une vente, identifiée par
`id_mutation`) occupe une ou plusieurs lignes :

```
Mutation (id_mutation)          prix, date, nature de la vente
 └── Parcelle (id_parcelle)     adresse, surface de terrain, coordonnées
      └── Local (type_local)    type, surface bâtie, nombre de pièces
```

| Niveau | Colonnes | Comportement dans le fichier |
|---|---|---|
| Mutation | `id_mutation`, `date_mutation`, `nature_mutation`, `valeur_fonciere` | répétées à l'identique sur chaque ligne de la vente |
| Parcelle | `id_parcelle`, adresse, `surface_terrain`, `longitude`, `latitude` | propres à chaque parcelle ; `surface_terrain` est répétée si la parcelle porte plusieurs locaux |
| Local | `type_local`, `surface_reelle_bati`, `nombre_pieces_principales` | propres à chaque ligne de local ; vides pour un terrain nu |

Exemple réel, extrait du fichier 2021 : la mutation `2021-2` occupe 5 lignes
(4 parcelles, 2 maisons, 1 dépendance, 2 petits terrains) pour un seul prix de 124 000 €.

### 1.2 Points d'attention pour le traitement

- **Prix** : `valeur_fonciere` est répété sur chaque ligne d'une mutation. Il faut le
  prendre une seule fois par `id_mutation`, sinon il est compté plusieurs fois.
- **Terrain** : `surface_terrain` se prend une fois par couple `id_mutation` + `id_parcelle`.
- **Bâti** : la surface et les pièces se somment sur les lignes `Maison` et
  `Appartement` uniquement. Les dépendances ont 0 m² et 0 pièce.
- **Mutations multi-logements** : un seul prix pour plusieurs logements ne permet pas de
  calculer un prix au m² fiable ; ces ventes sont à écarter.
- **Nature des transactions** : `nature_mutation` ne contient pas que des ventes
  (échanges, adjudications, etc.).
- **Terrains** : les ventes sans local (terres, bois, landes) ont souvent des prix très
  faibles et faussent les moyennes.
- **Codes en texte** : `code_departement` (par exemple `01`) et `code_postal` perdent
  leur zéro initial s'ils sont lus comme des nombres.
- **Colonnes souvent vides** : lots, anciens codes commune et parcelle, suffixe
  d'adresse, numéro de volume.
- **Coordonnées manquantes** : certaines lignes n'ont pas de latitude / longitude
  (géométrie de parcelle absente du cadastre, parcelle passée dans le domaine public).

### 1.3 Dictionnaire des colonnes

Le fichier contient 40 colonnes. Les noms ci-dessous suivent la documentation de la
livraison du 20/10/2026 ; l'en-tête exact du fichier téléchargé fait foi.

**Mutation**

| Colonne | Description |
|---|---|
| `id_mutation` | Identifiant de mutation (non stable d'une livraison à l'autre), sert à grouper les lignes |
| `date_mutation` | Date de la mutation, format ISO-8601 (AAAA-MM-JJ) |
| `numero_disposition` | Numéro de disposition |
| `nature_mutation` | Nature de la mutation |
| `valeur_fonciere` | Prix de la mutation en euros (séparateur décimal : point) |

**Adresse et localisation**

| Colonne | Description |
|---|---|
| `adresse_numero` | Numéro de l'adresse |
| `adresse_suffixe` | Suffixe du numéro de l'adresse (B, T, Q...) |
| `adresse_code_voie` | Code FANTOIR de la voie (4 caractères) |
| `adresse_nom_voie` | Nom de la voie |
| `code_postal` | Code postal (5 caractères, à lire en texte) |
| `code_commune` | Code commune INSEE actuel (5 caractères) |
| `nom_commune` | Nom actuel de la commune (accentué) |
| `ancien_code_commune` | Code INSEE d'origine, si différent du code actuel |
| `ancien_nom_commune` | Nom d'origine, si le code commune a changé |
| `code_departement` | Code département INSEE (2 ou 3 caractères, à lire en texte) |
| `longitude`, `latitude` | Centre de la parcelle concernée (WGS-84) |

**Parcelle**

| Colonne | Description |
|---|---|
| `id_parcelle` | Identifiant de parcelle actuel (14 caractères) |
| `ancien_id_parcelle` | Identifiant d'origine, si différent de l'actuel |
| `numero_volume` | Numéro de volume |
| `code_nature_culture`, `nature_culture` | Nature de la parcelle (code et libellé) |
| `code_nature_culture_speciale`, `nature_culture_speciale` | Nature de culture spéciale |
| `surface_terrain` | Surface du terrain |

**Local**

| Colonne | Description |
|---|---|
| `code_type_local`, `type_local` | Type de local (maison, appartement, dépendance...) ; vide pour un terrain |
| `surface_reelle_bati` | Surface réelle du bâti |
| `nombre_pieces_principales` | Nombre de pièces principales du logement |

**Lots (copropriété)**

| Colonne | Description |
|---|---|
| `nombre_lots` | Nombre de lots |
| `lot_1_numero` à `lot_5_numero` | Numéro de chaque lot (jusqu'à 5) |
| `lot_1_surface_carrez` à `lot_5_surface_carrez` | Surface Carrez de chaque lot |

### 1.4 Colonnes utilisées pour répondre à la question du persona

`id_mutation`, `date_mutation`, `nature_mutation`, `valeur_fonciere`,
`code_departement`, `code_commune`, `nom_commune`, `id_parcelle`, `type_local`,
`surface_reelle_bati`, `nombre_pieces_principales`, `surface_terrain`,
`longitude`, `latitude`.

## 2. Persona

**Claire, directrice du développement d'un réseau d'agences immobilières.**

- **Ce qu'elle décide :** dans quels départements ouvrir une nouvelle agence ou renforcer
  les équipes existantes.
- **À quelle fréquence :** chaque trimestre, lors du comité d'investissement.
- **Ce dont elle a besoin :** repérer rapidement les territoires où l'activité est
  réelle, sans que les prix ne soient déjà hors de portée de la clientèle de son réseau.

**Question principale :** dans quels départements le marché est-il actif (beaucoup de
ventes de logements) tout en restant accessible (prix médian au m² inférieur à la médiane
nationale), et comment cette activité évolue-t-elle mois par mois en 2022 ?

*Périmètre pressenti* : mutations de type vente, portant sur un seul logement (maison ou
appartement), avec prix et surface cohérents. Les règles de nettoyage exactes, avec le
nombre de lignes retirées par règle, seront documentées dans la couche silver.

## 3. Livrables prévus

| Étape | Contenu |
|---|---|
| Bronze | CSV brut en Delta dans RustFS, sans transformation |
| Silver | typage, nettoyage, une ligne par vente, tableau « règle / lignes retirées » |
| Gold | agrégats par département et par mois (nombre de ventes, prix médian au m²...), exportés dans PostgreSQL |
| Sémantique | ontologie `.ttl` (Mutation, Parcelle, Local, Commune...) et trois requêtes SPARQL |
| Visualisation | notebook d'exploration et un graphique avant / après justifié par les principes de perception |
| Tableau de bord | Streamlit/ou powerbi : 3 à 5 KPI avec fiches, récit contexte / constat / recommandation, au moins un filtre |
| Déploiement | lancement par `docker compose` |

## 4. Lancer le projet *(à compléter au fil de l'avancement)*

1. Cloner le dépôt.
2. Télécharger les données : `python scripts/download_dvf.py`
   (écrit `data/raw/full-2022.csv`, aucune clé requise).
3. Démarrer les services : `docker compose up -d`
4. Ouvrir Jupyter et exécuter les notebooks dans l'ordre.
5. Ouvrir le tableau de bord Streamlit.

## 5. Organisation du dépôt *(prévue)*

```
projet-dataviz-Leslie-Ashley/
├── README.md
├── docker-compose.yml
├── scripts/        téléchargement des données
├── notebooks/      bronze, silver, gold, SPARQL, exploration
├── ontology/       ontologie .ttl et requêtes SPARQL
├── dashboard/      application Streamlit
├── docs/           règles de nettoyage, fiches KPI
└── data/           données (non versionnées)
```

## 6. État d'avancement

- [x] Choix du jeu de données et du persona (echeance30/10)
- [ ] Script de téléchargement
- [ ] Bronze, silver, gold
- [ ] Ontologie et requêtes SPARQL
- [ ] Notebook d'exploration
- [ ] Tableau de bord powerbi