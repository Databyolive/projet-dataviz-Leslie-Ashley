"""Génère des pages HTML interactives (graphe qui bouge, zoom, survol) avec pyvis
Usage (depuis la racine du dépôt, dans le conteneur Jupyter) :
    pip install pyvis rdflib
    python semantique/generer_graphe_ontologie.py

Sorties :
    docs/ontologie_graphe.html   le schéma : classes, relations et attributs (toujours produit)
    docs/exemple_graphe.html     quelques ventes réelles du graphe RDF (produit si data/rdf/ventes_<dép>.ttl existe)
Il suffit ensuite d'ouvrir le fichier .html dans un navigateur.
"""
import json
from pathlib import Path

from pyvis.network import Network
from rdflib import Graph, Namespace, RDF, RDFS, OWL

RACINE = Path(__file__).resolve().parent.parent
TTL = RACINE / "ontology" / "dvf.ttl"
DEPARTEMENT = "33"                       # doit correspondre au notebook 04_sparql
DONNEES = RACINE / "data" / "rdf" / f"ventes_{DEPARTEMENT}.ttl"
NB_VENTES_EXEMPLE = 25                   # nombre de ventes dessinées dans le graphe d'exemple

DVF = Namespace("https://example.org/dvf#")
COULEURS = {"Mutation": "#4C72B0", "Logement": "#DD8452", "Maison": "#55A868", "Appartement": "#C44E52",
            "Parcelle": "#8172B3", "Commune": "#937860", "Departement": "#222222"}
OPTIONS = {
    "physics": {"solver": "forceAtlas2Based",
                "forceAtlas2Based": {"gravitationalConstant": -60, "centralGravity": 0.01, "springLength": 130,
                                     "springConstant": 0.08, "avoidOverlap": 0.6},
                "stabilization": {"iterations": 300}},
    "interaction": {"hover": True, "navigationButtons": True, "tooltipDelay": 100},
}


def nom(uri):
    return str(uri).split("#")[-1].split("/")[-1]


def libelle(g, s):
    v = g.value(s, RDFS.label)
    return str(v) if v else nom(s)


def nouveau_reseau():
    net = Network(height="800px", width="100%", directed=True, bgcolor="#ffffff", font_color="#222222",
                  cdn_resources="in_line")
    net.set_options(json.dumps(OPTIONS))
    return net


def ecrire(net, chemin):
    chemin.parent.mkdir(parents=True, exist_ok=True)

    html = net.generate_html(notebook=False)

    if not html or len(html) < 1000:
        raise ValueError("Le HTML généré est vide ou incomplet.")

    with open(chemin, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Écrit : {chemin.relative_to(RACINE)}")
    print(f"Taille du fichier : {chemin.stat().st_size} octets")


def graphe_ontologie(g):
    net = nouveau_reseau()
    classes = {nom(s): s for s in g.subjects(RDF.type, OWL.Class)}
    attributs = {}
    for p in g.subjects(RDF.type, OWL.DatatypeProperty):
        attributs.setdefault(nom(g.value(p, RDFS.domain)), []).append((libelle(g, p), nom(g.value(p, RDFS.range))))

    for n, uri in classes.items():
        lignes = [libelle(g, uri), str(g.value(uri, RDFS.comment) or "")] + [f"- {a} : {t}" for a, t in attributs.get(n, [])]
        net.add_node(n, label=libelle(g, uri), color=COULEURS.get(n, "#888888"), size=32, shape="dot",
                     title="\n".join(l for l in lignes if l), font={"size": 24, "strokeWidth": 5, "strokeColor": "#ffffff"})
    for n, liste in attributs.items():       # un petit point par attribut, relié à sa classe
        for a, t in liste:
            idn = f"{n}.{a}"
            net.add_node(idn, label=a, color="#BBBBBB", size=8, shape="dot", title=f"{a} ({t})",
                         font={"size": 14, "strokeWidth": 4, "strokeColor": "#ffffff"})
            net.add_edge(n, idn, color="#DDDDDD", width=0.8, arrows="")
    for p in g.subjects(RDF.type, OWL.ObjectProperty):
        net.add_edge(nom(g.value(p, RDFS.domain)), nom(g.value(p, RDFS.range)), label=libelle(g, p),
                     color="#444444", width=2.5, font={"size": 16, "strokeWidth": 4, "strokeColor": "#ffffff"})
    for enfant, parent in g.subject_objects(RDFS.subClassOf):
        net.add_edge(nom(enfant), nom(parent), label="est un type de", dashes=True, color="#888888", width=2,
                     font={"size": 14, "strokeWidth": 4, "strokeColor": "#ffffff"})
    ecrire(net, RACINE / "docs" / "ontologie_graphe.html")


def graphe_exemple(onto):
    if not DONNEES.exists():
        print(f"Pas de graphe d'exemple : {DONNEES.relative_to(RACINE)} n'existe pas (lancer d'abord le notebook 04_sparql).")
        return
    g = Graph().parse(DONNEES, format="turtle")
    net = nouveau_reseau()
    vues = set()

    def noeud(uri, classe, label, titre, taille):
        if str(uri) not in vues:
            vues.add(str(uri))
            net.add_node(str(uri), label=label, color=COULEURS[classe], size=taille, shape="dot", title=titre,
                         font={"size": 14, "strokeWidth": 4, "strokeColor": "#ffffff"})

    mutations = sorted(g.subjects(RDF.type, DVF.Mutation))[:NB_VENTES_EXEMPLE]
    for m in mutations:
        prix_m2 = g.value(m, DVF.prixAuM2)
        valeur = g.value(m, DVF.valeurFonciere)
        noeud(m, "Mutation", f"{float(prix_m2):.0f} €/m²" if prix_m2 else "vente",
              f"Vente\nvaleur : {valeur} €\nprix au m² : {prix_m2}\ndate : {g.value(m, DVF.dateMutation)}", 14)
        for l in g.objects(m, DVF.portesSur):
            classe = "Maison" if (l, RDF.type, DVF.Maison) in g else "Appartement"
            noeud(l, classe, classe, f"{classe}\nsurface : {g.value(l, DVF.surfaceBati)} m²\npièces : {g.value(l, DVF.nombrePieces)}", 10)
            net.add_edge(str(m), str(l), color="#999999", width=1)
            for p in g.objects(l, DVF.situeSurParcelle):
                noeud(p, "Parcelle", "", f"Parcelle {nom(p)}", 6)
                net.add_edge(str(l), str(p), color="#BBBBBB", width=0.8)
                for c in g.objects(p, DVF.situeeDans):
                    noeud(c, "Commune", str(g.value(c, DVF.nomCommune)), f"Commune : {g.value(c, DVF.nomCommune)}", 26)
                    net.add_edge(str(p), str(c), color="#BBBBBB", width=0.8)
                    for d in g.objects(c, DVF.appartientA):
                        noeud(d, "Departement", f"Dép. {g.value(d, DVF.codeDepartement)}", "Département", 40)
                        net.add_edge(str(c), str(d), color="#888888", width=2)
    ecrire(net, RACINE / "docs" / "exemple_graphe.html")


def main():
    onto = Graph().parse(TTL, format="turtle")
    graphe_ontologie(onto)
    graphe_exemple(onto)


if __name__ == "__main__":
    main()