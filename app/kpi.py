"""Les cinq indicateurs (KPI) du tableau de bord : fiches (définition, calcul, intérêt) et calculs."""

NBSP = "\u00a0"


def fmt_int(x) -> str:
    return f"{x:,.0f}".replace(",", NBSP)


def fmt_eur(x) -> str:
    return f"{fmt_int(x)}{NBSP}€"


def fmt_pct(x, signe=True) -> str:
    texte = f"{x:+.1f}" if signe else f"{x:.1f}"
    return texte.replace(".", ",").replace("-", "−") + f"{NBSP}%"


FICHES = {
    "ventes": {
        "titre": "Ventes de logements", "icone": "ventes", "couleur": "#1B6CA8",
        "definition": "Nombre de ventes de logements (maisons et appartements) enregistrées dans le département en 2025, après nettoyage des données.",
        "calcul": "Comptage des ventes de la table silver `ventes_dvf_2025` (une ligne par vente), regroupées par département et type de bien. Table gold : `gold_departement.nb_ventes`.",
        "interet": "Mesure l’**activité** du marché. Pour Claire, un département où l’on vend beaucoup est un département où une agence a du travail et peut atteindre rapidement un volume d’affaires.",
        "lecture": "Un grand département compte mécaniquement plus de ventes : à lire avec le prix et l’écart à la médiane. Seuil de fiabilité : un département sous le seuil est signalé.",
    },
    "prix_m2": {
        "titre": "Prix au m² médian", "icone": "prix_m2", "couleur": "#D1495B",
        "definition": "Prix de vente au mètre carré habitable : la moitié des ventes du département se font en dessous de cette valeur, l’autre moitié au-dessus.",
        "calcul": "Pour chaque vente : valeur foncière ÷ surface bâtie du logement. On prend la **médiane** (exacte, `F.median` dans Spark) par département. Table gold : `gold_departement.prix_m2_median`.",
        "interet": "Donne le **niveau de prix** du marché indépendamment de la taille des biens. C’est la base de la comparaison entre départements.",
        "lecture": "La médiane résiste aux ventes extrêmes. Les ventes de moins de 500 € ou plus de 30 000 € par m² ont été écartées lors du nettoyage.",
    },
    "ecart": {
        "titre": "Écart à la médiane nationale", "icone": "ecart", "couleur": "#13A89E",
        "definition": "Écart relatif entre le prix au m² médian du département et le prix au m² médian de la France entière (même type de bien).",
        "calcul": "`prix_m2_median_département ÷ prix_m2_median_national − 1`. Table gold : `gold_departement.ecart_national`. Négatif = moins cher que la France.",
        "interet": "Traduit le mot **« accessible »** de la question de Claire : un département est accessible s’il est moins cher que la médiane nationale. Il se lit sans connaître les prix de mémoire.",
        "lecture": "Un écart de −20 % veut dire : prix au m² médian inférieur de 20 % à celui de la France. Paris, très au-dessus, sature l’échelle de la carte.",
    },
    "prix_median": {
        "titre": "Prix médian d’une vente", "icone": "prix_median", "couleur": "#F4A259",
        "definition": "Montant en euros d’une vente typique dans le département : la moitié des ventes sont conclues en dessous, l’autre moitié au-dessus.",
        "calcul": "Médiane de la valeur foncière des ventes de logements par département (et surface médiane associée). Table gold : `gold_departement.prix_median` et `surface_mediane`.",
        "interet": "Complète le prix au m² : c’est le **montant réel** d’une transaction, utile pour estimer le chiffre d’affaires d’une agence à partir d’une vente moyenne.",
        "lecture": "Un prix médian élevé peut venir de grandes surfaces autant que de prix élevés : la surface médiane est affichée à côté.",
    },
    "evolution": {
        "titre": "Évolution de l’activité (2ᵉ vs 1er semestre)", "icone": "evolution", "couleur": "#6C5CE7",
        "definition": "Variation du nombre de ventes entre le 2ᵉ semestre (juillet à décembre) et le 1er semestre (janvier à juin) 2025.",
        "calcul": "`ventes_S2 ÷ ventes_S1 − 1`, calculé à partir de `gold_departement_mois.nb_ventes`. Positif = le marché s’anime dans l’année.",
        "interet": "Répond à la seconde moitié de la question de Claire : **comment le marché évolue-t-il mois par mois**. Un marché qui accélère justifie d’ouvrir plus tôt.",
        "lecture": "Une seule année : la saisonnalité (creux de mai, pic de juillet au niveau national) et le décalage de saisie des actes pèsent sur la lecture. Ce n’est pas une prévision.",
    },
}


def evolution_s2_s1(mois_dep):
    """Variation en % des ventes du 2ᵉ semestre par rapport au 1er (None si impossible)."""
    s1 = mois_dep.loc[mois_dep["mois"] <= 6, "nb_ventes"].sum()
    s2 = mois_dep.loc[mois_dep["mois"] >= 7, "nb_ventes"].sum()
    if s1 == 0:
        return None
    return (s2 / s1 - 1) * 100


def valeurs(ligne, mois_dep, mediane_ventes):
    """Valeur et commentaire de chacun des cinq KPI pour un département."""
    evo = evolution_s2_s1(mois_dep)
    return {
        "ventes": (fmt_int(ligne["nb_ventes"]), f"médiane des départements : {fmt_int(mediane_ventes)}"),
        "prix_m2": (fmt_eur(ligne["prix_m2_median"]) + "/m²", f"France : {fmt_eur(ligne['prix_m2_median_national'])}/m²"),
        "ecart": (fmt_pct(ligne["ecart_pct"]), "moins cher que la France" if ligne["ecart_pct"] < 0 else "plus cher que la France"),
        "prix_median": (fmt_eur(ligne["prix_median"]), f"surface médiane : {fmt_int(ligne['surface_mediane'])}{NBSP}m²"),
        "evolution": (fmt_pct(evo) if evo is not None else "n.d.", "ventes S2 contre S1"),
    }


def fiche_markdown(cle: str) -> str:
    f = FICHES[cle]
    return (f"# KPI : {f['titre']}\n\n"
            f"## Définition\n{f['definition']}\n\n"
            f"## Calcul\n{f['calcul']}\n\n"
            f"## Intérêt pour le persona (Claire, directrice du développement d’un réseau d’agences)\n{f['interet']}\n\n"
            f"## Lecture et limites\n{f['lecture']}\n")
