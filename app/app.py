"""Tableau de bord DVF 2025 : où ouvrir une agence ? Récit en trois temps : contexte, constat, recommandation."""
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import donnees
import illustrations as il
import kpi

st.set_page_config(page_title="DVF 2025 · Où ouvrir une agence ?", page_icon="🏠", layout="wide")

MOIS = ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."]
BLEU, ROUGE, VERT, ORANGE, GRIS, ENCRE = "#1B6CA8", "#D1495B", "#13A89E", "#F4A259", "#B8C2D0", "#0B2545"

st.markdown("""
<style>
#MainMenu, footer {visibility: hidden;}
.block-container {padding-top: 1.4rem; max-width: 1280px;}
html, body, [class*="css"] {font-family: "Inter", "Segoe UI", system-ui, sans-serif;}
.hero {display: flex; gap: 2rem; align-items: center; background: linear-gradient(120deg, #0B2545 0%, #16325C 55%, #1B6CA8 100%);
       border-radius: 24px; padding: 2rem 2.4rem; color: #fff; box-shadow: 0 18px 40px rgba(11,37,69,.25);}
.hero h1 {font-size: 2.3rem; line-height: 1.15; margin: 0 0 .6rem 0; color: #fff;}
.hero p {margin: .25rem 0; color: #D9E4F5; font-size: 1.02rem;}
.hero .badge {display: inline-block; background: rgba(255,255,255,.14); border-radius: 999px; padding: .25rem .8rem; margin: .5rem .4rem 0 0; font-size: .85rem;}
.hero .illu {flex: 0 0 46%; border-radius: 18px; overflow: hidden;}
.chapitre {display: flex; align-items: center; gap: 1rem; margin: 2.4rem 0 .4rem 0;}
.chapitre h2 {margin: 0; font-size: 1.6rem; color: #0B2545;}
.chapitre .num {font-size: .8rem; letter-spacing: .12em; text-transform: uppercase; color: #5D6B82;}
.tuile {background: #fff; border-radius: 18px; padding: 1rem 1.2rem; box-shadow: 0 6px 20px rgba(11,37,69,.08); border-top: 5px solid var(--accent);}
.tuile .valeur {font-size: 1.8rem; font-weight: 800; color: #0B2545;}
.tuile .libelle {color: #5D6B82; font-size: .9rem;}
.kpi {background: #fff; border-radius: 20px; padding: 1rem 1.1rem 1.1rem 1.1rem; box-shadow: 0 8px 24px rgba(11,37,69,.10); border-bottom: 5px solid var(--accent); height: 100%;}
.kpi .tete {display: flex; align-items: center; gap: .7rem;}
.kpi .titre {font-weight: 700; font-size: .92rem; color: #0B2545; line-height: 1.2;}
.kpi .valeur {font-size: 1.85rem; font-weight: 800; margin: .5rem 0 .1rem 0; color: var(--accent);}
.kpi .sous {color: #5D6B82; font-size: .82rem;}
.retenir {background: #EAF3FB; border-left: 6px solid #1B6CA8; border-radius: 12px; padding: .8rem 1.1rem; color: #0B2545; margin: .6rem 0 1rem 0;}
.verdict {border-radius: 18px; padding: 1.1rem 1.4rem; color: #fff; font-size: 1.08rem; margin: .4rem 0 1.2rem 0;}
.verdict.oui {background: linear-gradient(120deg, #0E8F86, #13A89E);} .verdict.peut {background: linear-gradient(120deg, #C98324, #F4A259);}
.verdict.non {background: linear-gradient(120deg, #8D3345, #D1495B);}
.verdict b {font-size: 1.25rem;}
</style>
""", unsafe_allow_html=True)


def chapitre(numero, titre, icone_nom, sous_titre):
    st.markdown(f'<div class="chapitre">{il.icone(icone_nom, 60)}<div><div class="num">Chapitre {numero}</div><h2>{titre}</h2></div></div>', unsafe_allow_html=True)
    st.caption(sous_titre)


def a_retenir(texte):
    st.markdown(f'<div class="retenir"><b>À retenir.</b> {texte}</div>', unsafe_allow_html=True)


def habiller(fig, titre, hauteur=380):
    fig.update_layout(title=dict(text=titre, x=0, font=dict(size=16, color=ENCRE)), height=hauteur, template="simple_white",
                      margin=dict(l=10, r=10, t=60, b=10), separators=", ", font=dict(family="Inter, Segoe UI, sans-serif", color=ENCRE),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    return fig


# ------------------------------------------------------------------ données
try:
    dep, mois, nat = donnees.charger()
except Exception as erreur:  # base injoignable ou tables absentes
    st.error("Impossible de lire les tables gold dans PostgreSQL. Vérifiez que `docker compose up` est lancé et que le notebook 03_gold a été exécuté.")
    st.exception(erreur)
    st.stop()

noms = donnees.noms_departements()
geo = donnees.geojson_metropole()

# ------------------------------------------------------------------ filtres (barre latérale)
with st.sidebar:
    st.markdown("### 🎛️ Filtres")
    type_bien = st.radio("Type de bien", ["Tous", "Maison", "Appartement"], help="Les prix diffèrent beaucoup entre maisons et appartements.")
    centile = st.slider("Seuil d’activité : un département est « actif » au-dessus du centile…", 0, 90, 50, 5,
                        help="50 = au-dessus de la médiane des départements. À augmenter pour être plus exigeant.")
    fiables = st.toggle("Masquer les départements peu fiables", value=True, help="Un département est peu fiable s’il compte trop peu de ventes pour une médiane stable.")

d_tous = dep[dep["type_bien"] == type_bien].copy()
d = d_tous[d_tous["fiable"]] if fiables else d_tous
if d.empty:
    st.warning("Aucun département pour ce filtre.")
    st.stop()

mediane_nat = d_tous["prix_m2_median_national"].iloc[0]
seuil_actif = d["nb_ventes"].quantile(centile / 100)
d = d.assign(actif=d["nb_ventes"] > seuil_actif, accessible=d["ecart_national"] < 0)
d = d.assign(reco=d["actif"] & d["accessible"])
reco = d[d["reco"]].sort_values("ecart_national")

options = sorted(d_tous["code_departement"].unique(), key=lambda c: noms.get(c, c))
if "dep_choisi" not in st.session_state:
    st.session_state["dep_choisi"] = reco.sort_values("nb_ventes", ascending=False)["code_departement"].iloc[0] if len(reco) else options[0]
with st.sidebar:
    code = st.selectbox("Département à analyser", options, key="dep_choisi", format_func=lambda c: f"{c} · {noms.get(c, c)}")
    st.markdown("---")
    st.caption("Source : demandes de valeurs foncières (DVF) 2025, Etalab / DGFiP. Traitement : Spark, Delta Lake, PostgreSQL.")

nat_t = nat[nat["type_bien"] == type_bien].sort_values("mois")
total_ventes = int(nat_t["nb_ventes"].sum())

# ------------------------------------------------------------------ bandeau
st.markdown(f"""
<div class="hero">
  <div>
    <h1>Où ouvrir sa prochaine agence immobilière&nbsp;?</h1>
    <p>Le marché des logements en France en 2025, vu par <b>Claire</b>, directrice du développement d’un réseau d’agences.
       Sa question : <i>dans quels départements le marché est-il actif et accessible, et comment évolue-t-il mois par mois&nbsp;?</i></p>
    <span class="badge">🏠 {kpi.fmt_int(total_ventes)} ventes de logements</span>
    <span class="badge">📍 {d_tous['code_departement'].nunique()} départements</span>
    <span class="badge">📅 janvier à décembre 2025</span>
  </div>
  <div class="illu">{il.en_image(il.bandeau(), alt="Illustration de maisons et d’immeubles")}</div>
</div>
""", unsafe_allow_html=True)

# ================================================================== 1. CONTEXTE
chapitre(1, "Contexte : le marché français en 2025", "contexte", "Les ordres de grandeur nationaux, avant de comparer les départements.")
mois_pic = nat_t.loc[nat_t["nb_ventes"].idxmax()]
mois_creux = nat_t.loc[nat_t["nb_ventes"].idxmin()]
c1, c2, c3, c4 = st.columns(4)
for colonne, valeur, libelle, couleur in [
    (c1, kpi.fmt_int(total_ventes), "ventes de logements retenues", BLEU),
    (c2, kpi.fmt_eur(mediane_nat) + "/m²", "prix au m² médian national", ROUGE),
    (c3, MOIS[int(mois_pic["mois"]) - 1], f"mois le plus actif ({kpi.fmt_int(mois_pic['nb_ventes'])} ventes)", VERT),
    (c4, MOIS[int(mois_creux["mois"]) - 1], f"mois le plus calme ({kpi.fmt_int(mois_creux['nb_ventes'])} ventes)", ORANGE),
]:
    colonne.markdown(f'<div class="tuile" style="--accent:{couleur}"><div class="valeur">{valeur}</div><div class="libelle">{libelle}</div></div>', unsafe_allow_html=True)

g1, g2 = st.columns(2)
couleurs = [ROUGE if m == mois_creux["mois"] else (VERT if m == mois_pic["mois"] else BLEU) for m in nat_t["mois"]]
f1 = go.Figure(go.Bar(x=[MOIS[int(m) - 1] for m in nat_t["mois"]], y=nat_t["nb_ventes"], marker_color=couleurs,
                      hovertemplate="%{x} : %{y:,.0f} ventes<extra></extra>"))
f1.update_yaxes(title="Ventes de logements", rangemode="tozero")
g1.plotly_chart(habiller(f1, f"L’activité culmine en {MOIS[int(mois_pic['mois']) - 1]} et fléchit en {MOIS[int(mois_creux['mois']) - 1]}"), width="stretch")
f2 = go.Figure(go.Scatter(x=[MOIS[int(m) - 1] for m in nat_t["mois"]], y=nat_t["prix_m2_median"], mode="lines+markers",
                          line=dict(color=ROUGE, width=3), marker=dict(size=8), hovertemplate="%{x} : %{y:,.0f} €/m²<extra></extra>"))
f2.update_yaxes(title="Prix au m² médian (€)")
g2.plotly_chart(habiller(f2, "Le prix au m² médian national varie peu d’un mois à l’autre"), width="stretch")
a_retenir(f"Sur l’année, {kpi.fmt_int(total_ventes)} logements ont été vendus. L’activité varie fortement d’un mois à l’autre "
          f"({kpi.fmt_int(mois_creux['nb_ventes'])} ventes en {MOIS[int(mois_creux['mois']) - 1]}, {kpi.fmt_int(mois_pic['nb_ventes'])} en {MOIS[int(mois_pic['mois']) - 1]}) : "
          "il faudra en tenir compte avant de lire une évolution mensuelle.")

# ================================================================== 2. CONSTAT
chapitre(2, "Constat : où le marché est-il actif et accessible ?", "constat", "Deux lectures de la même réalité : la carte (où ?) et le nuage de points (activité contre prix).")
metrique = st.radio("Colorier la carte selon", ["Écart à la médiane nationale", "Prix au m² médian", "Nombre de ventes"], horizontal=True)
carte = d[d["code_departement"].isin({f["properties"]["code"] for f in geo["features"]})].copy()
choix = {"Écart à la médiane nationale": ("ecart_pct", "Écart (%)", px.colors.diverging.RdBu_r, (-50, 50)),
         "Prix au m² médian": ("prix_m2_median", "€/m²", px.colors.sequential.YlOrRd, None),
         "Nombre de ventes": ("nb_ventes", "Ventes", px.colors.sequential.Blues, None)}
colonne_couleur, titre_barre, palette, plage = choix[metrique]
m, s = st.columns([1.05, 1])
fig_carte = px.choropleth(carte, geojson=geo, locations="code_departement", featureidkey="properties.code", color=colonne_couleur,
                          color_continuous_scale=palette, range_color=plage, color_continuous_midpoint=0 if plage else None,
                          hover_name="departement", custom_data=["nb_ventes", "prix_m2_median", "ecart_pct"])
fig_carte.update_traces(hovertemplate="<b>%{hovertext}</b><br>Ventes : %{customdata[0]:,.0f}<br>Prix : %{customdata[1]:,.0f} €/m²<br>Écart : %{customdata[2]:+.0f} %<extra></extra>",
                        marker_line_color="#FFFFFF", marker_line_width=0.6)
if code in set(carte["code_departement"]):
    fig_carte.add_trace(go.Choropleth(geojson=geo, locations=[code], z=[1], featureidkey="properties.code", showscale=False, hoverinfo="skip",
                                      colorscale=[[0, "rgba(0,0,0,0)"], [1, "rgba(0,0,0,0)"]], marker_line_color=ENCRE, marker_line_width=3))
fig_carte.update_geos(fitbounds="locations", visible=False)
fig_carte.update_layout(coloraxis_colorbar=dict(title=titre_barre, thickness=12, len=0.7))
m.plotly_chart(habiller(fig_carte, f"{metrique} par département (métropole)", 520), width="stretch")
m.caption("Contour foncé : département analysé. Les départements d’outre-mer et ceux masqués par le filtre ne sont pas dessinés. Échelle de la carte de l’écart bornée à ±50 % : Paris la dépasse.")

d_pts = d.assign(groupe=d["reco"].map({True: "Actif et accessible", False: "Autres départements"}))
nuage = px.scatter(d_pts, x="nb_ventes", y="ecart_pct", color="groupe", log_x=True, hover_name="departement",
                   color_discrete_map={"Actif et accessible": VERT, "Autres départements": GRIS}, custom_data=["prix_m2_median"])
nuage.update_traces(marker=dict(size=11, line=dict(width=1, color="#fff")),
                    hovertemplate="<b>%{hovertext}</b><br>Ventes : %{x:,.0f}<br>Écart : %{y:+.0f} %<br>Prix : %{customdata[0]:,.0f} €/m²<extra></extra>")
nuage.add_hline(y=0, line_color=ENCRE, line_width=1)
nuage.add_vline(x=seuil_actif, line_color=ENCRE, line_width=1, line_dash="dash")
nuage.add_annotation(x=1, y=0, xref="paper", yref="y", text="plus cher que la France ↑  /  moins cher ↓", showarrow=False, xanchor="right", yanchor="bottom", font=dict(size=11, color="#5D6B82"))
for _, r in reco.nlargest(6, "nb_ventes").iterrows():
    nuage.add_annotation(x=r["nb_ventes"], y=r["ecart_pct"], text=r["departement"], showarrow=False, yshift=14, font=dict(size=11, color=ENCRE))
sel = d[d["code_departement"] == code]
if len(sel):
    nuage.add_trace(go.Scatter(x=sel["nb_ventes"], y=sel["ecart_pct"], mode="markers", showlegend=False, hoverinfo="skip",
                               marker=dict(size=22, color="rgba(0,0,0,0)", line=dict(width=3, color=ENCRE))))
nuage.update_xaxes(title="Nombre de ventes (échelle logarithmique)")
nuage.update_yaxes(title="Écart du prix au m² à la médiane nationale (%)")
nuage.update_layout(legend=dict(orientation="h", y=-0.22, title=None))
s.plotly_chart(habiller(nuage, f"{len(reco)} départements sont actifs et moins chers que la France", 520), width="stretch")
s.caption("Trait vertical en pointillés : seuil d’activité (réglable dans la barre latérale). Cercle foncé : département analysé.")

plus_chers = d.nlargest(3, "prix_m2_median")["departement"].tolist()
moins_chers = d.nsmallest(3, "prix_m2_median")["departement"].tolist()
a_retenir(f"<b>{len(reco)} départements</b> sur {len(d)} sont à la fois actifs (plus de {kpi.fmt_int(seuil_actif)} ventes) et accessibles (prix au m² sous la médiane nationale de {kpi.fmt_eur(mediane_nat)}). "
          f"Les plus chers sont {', '.join(plus_chers)} ; les moins chers {', '.join(moins_chers)}. Les moins chers sont rarement les plus actifs : c’est tout l’enjeu du choix.")

# ================================================================== 3. RECOMMANDATION
chapitre(3, "Recommandation : quels départements étudier en priorité ?", "recommandation", "La liste des départements actifs et accessibles, puis le détail du département choisi dans la barre latérale.")
ligne = d_tous[d_tous["code_departement"] == code]
if ligne.empty:
    st.warning("Ce département n’a pas de ventes pour ce type de bien.")
    st.stop()
ligne = ligne.iloc[0]
est_actif = ligne["nb_ventes"] > seuil_actif
est_accessible = ligne["ecart_national"] < 0
nom = noms.get(code, code)
if est_actif and est_accessible:
    cls, titre_verdict = "oui", "À étudier en priorité"
    phrase = f"{nom} est <b>actif</b> ({kpi.fmt_int(ligne['nb_ventes'])} ventes) et <b>accessible</b> ({kpi.fmt_pct(ligne['ecart_pct'])} par rapport au prix national)."
elif est_actif:
    cls, titre_verdict = "peut", "Actif mais cher"
    phrase = f"{nom} est actif ({kpi.fmt_int(ligne['nb_ventes'])} ventes) mais plus cher que la France ({kpi.fmt_pct(ligne['ecart_pct'])}) : un marché porteur, à investissement élevé."
elif est_accessible:
    cls, titre_verdict = "peut", "Accessible mais peu actif"
    phrase = f"{nom} est moins cher que la France ({kpi.fmt_pct(ligne['ecart_pct'])}) mais compte peu de ventes ({kpi.fmt_int(ligne['nb_ventes'])}) : un marché abordable, à faible volume."
else:
    cls, titre_verdict = "non", "Pas prioritaire"
    phrase = f"{nom} est à la fois peu actif ({kpi.fmt_int(ligne['nb_ventes'])} ventes) et plus cher que la France ({kpi.fmt_pct(ligne['ecart_pct'])})."
if not ligne["fiable"]:
    phrase += " <i>Attention : peu de ventes, médiane peu fiable.</i>"
st.markdown(f'<div class="verdict {cls}"><b>{titre_verdict}</b><br>{phrase}</div>', unsafe_allow_html=True)

st.markdown(f"#### Les cinq indicateurs de {nom}")
mois_dep = mois[(mois["code_departement"] == code) & (mois["type_bien"] == type_bien)].sort_values("mois")
vals = kpi.valeurs(ligne, mois_dep, d_tous["nb_ventes"].median())
colonnes = st.columns(5)
for colonne, cle in zip(colonnes, kpi.FICHES):
    f = kpi.FICHES[cle]
    valeur, sous = vals[cle]
    colonne.markdown(f'<div class="kpi" style="--accent:{f["couleur"]}"><div class="tete">{il.icone(f["icone"], 44)}<div class="titre">{f["titre"]}</div></div>'
                     f'<div class="valeur">{valeur}</div><div class="sous">{sous}</div></div>', unsafe_allow_html=True)
    with colonne.popover("📖 Fiche du KPI", width="stretch"):
        st.markdown(f"**{f['titre']}**")
        st.markdown(f"**Définition.** {f['definition']}")
        st.markdown(f"**Calcul.** {f['calcul']}")
        st.markdown(f"**Intérêt pour Claire.** {f['interet']}")
        st.caption(f["lecture"])

st.markdown("#### Évolution mois par mois")
if len(mois_dep):
    profil = nat_t.set_index("mois")["nb_ventes"].reindex(mois_dep["mois"])
    profil = profil / nat_t["nb_ventes"].sum() * mois_dep["nb_ventes"].sum()
    couleurs_m = [BLEU if ok else GRIS for ok in mois_dep["fiable"]]
    fm = go.Figure()
    fm.add_trace(go.Bar(x=[MOIS[int(x) - 1] for x in mois_dep["mois"]], y=mois_dep["nb_ventes"], name=nom, marker_color=couleurs_m,
                        hovertemplate="%{x} : %{y:,.0f} ventes<extra></extra>"))
    fm.add_trace(go.Scatter(x=[MOIS[int(x) - 1] for x in mois_dep["mois"]], y=profil.values, name="Profil national (mis à l’échelle)", mode="lines+markers",
                            line=dict(color=ORANGE, width=3), hovertemplate="Profil national : %{y:,.0f}<extra></extra>"))
    fm.update_yaxes(title="Ventes de logements", rangemode="tozero")
    fm.update_layout(legend=dict(orientation="h", y=-0.18))
    evo = kpi.evolution_s2_s1(mois_dep)
    st.plotly_chart(habiller(fm, f"{nom} suit-il la saisonnalité nationale ? ({kpi.fmt_pct(evo) if evo is not None else 'n.d.'} au 2ᵉ semestre)"), width="stretch")
    st.caption("Barres grises : mois avec trop peu de ventes pour être fiables. La ligne orange est le profil mensuel de la France, ramené au volume du département : elle sert de repère.")

st.markdown("#### Les départements actifs et accessibles")
if len(reco):
    tableau = reco[["code_departement", "departement", "nb_ventes", "prix_m2_median", "ecart_pct", "prix_median"]].rename(columns={
        "code_departement": "Code", "departement": "Département", "nb_ventes": "Ventes", "prix_m2_median": "Prix au m²", "ecart_pct": "Écart national", "prix_median": "Prix médian d’une vente"})
    st.dataframe(tableau, hide_index=True, width="stretch", column_config={
        "Ventes": st.column_config.ProgressColumn("Ventes", format="%d", min_value=0, max_value=int(d["nb_ventes"].max())),
        "Prix au m²": st.column_config.NumberColumn(format="%d €"),
        "Écart national": st.column_config.NumberColumn(format="%+.1f %%"),
        "Prix médian d’une vente": st.column_config.NumberColumn(format="%d €")})
    a_retenir(f"Trié du plus accessible au moins accessible : <b>{reco.iloc[0]['departement']}</b> a l’écart le plus favorable ({kpi.fmt_pct(reco.iloc[0]['ecart_pct'])}), "
              f"<b>{reco.sort_values('nb_ventes').iloc[-1]['departement']}</b> est le plus actif ({kpi.fmt_int(reco['nb_ventes'].max())} ventes). "
              "Le choix final dépend de la priorité de Claire : volume d’affaires ou ticket d’entrée.")
else:
    st.info("Aucun département ne remplit les deux conditions avec ce seuil d’activité : baissez le seuil dans la barre latérale.")

with st.expander("Méthode, limites et sources"):
    st.markdown("""
- **Source** : demandes de valeurs foncières géolocalisées 2025 (Etalab, DGFiP), jeu ouvert. Filtres appliqués : ventes uniquement, un seul logement par vente, prix au m² entre 500 € et 30 000 € (voir `docs/regles_silver.md`).
- **Médianes exactes** par département, calculées avec Spark, stockées dans Delta Lake puis exportées vers PostgreSQL.
- **Couverture** : la base DVF ne couvre ni l’Alsace-Moselle (Bas-Rhin, Haut-Rhin, Moselle) ni Mayotte. Les départements d’outre-mer figurent dans les tables mais pas sur la carte.
- **Une seule année** : les évolutions sont des constats, pas des prévisions.
- **Contours des départements** : fichier simplifié du dépôt `gregoiredavid/france-geojson`. Illustrations dessinées pour le projet.
""")