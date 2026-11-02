"Source	https://www.data.gouv.fr/datasets/demandes-de-valeurs-foncieres-geolocalisees"



import gzip
import hashlib
import shutil
import urllib.request
from pathlib import Path

RESSOURCES = {
    2025: {
        "id": "b3a0c6d2-2a5a-45a3-81a8-9e860caf5e14",
        "sha1": "3f01863b4913bf2d45e5331959e935e1a224b107",
    },
}
ANNEES = [2025]

DEST = Path(__file__).resolve().parent.parent / "data" / "raw"


def url_stable(identifiant: str) -> str:
    return f"https://www.data.gouv.fr/api/1/datasets/r/{identifiant}"


def sha1(chemin: Path) -> str:
    h = hashlib.sha1()
    with open(chemin, "rb") as f:
        for bloc in iter(lambda: f.read(1024 * 1024), b""):
            h.update(bloc)
    return h.hexdigest()


def telecharger(annee: int) -> None:
    ressource = RESSOURCES[annee]
    sortie = DEST / f"full-{annee}.csv"
    archive = DEST / f"full-{annee}.csv.gz"
    temporaire = DEST / f"full-{annee}.csv.part"

    if sortie.exists():
        print(f"[{annee}] {sortie.name} existe déjà, rien à faire.")
        return

    DEST.mkdir(parents=True, exist_ok=True)
    print(f"[{annee}] Téléchargement en cours...")
    urllib.request.urlretrieve(url_stable(ressource["id"]), archive)
    empreinte_archive = sha1(archive)

    print(f"[{annee}] Décompression...")
    with gzip.open(archive, "rb") as src, open(temporaire, "wb") as dst:
        shutil.copyfileobj(src, dst)
    temporaire.replace(sortie) 
    if empreinte_archive == ressource["sha1"]:
        print(f"[{annee}] Empreinte sha1 conforme (archive).")
    elif sha1(sortie) == ressource["sha1"]:
        print(f"[{annee}] Empreinte sha1 conforme (CSV).")
    else:
        print(f"[{annee}] ATTENTION : empreinte sha1 différente de celle de data.gouv.fr "
              "(fichier peut-être mis à jour, ou corrompu).")

    archive.unlink()
    print(f"[{annee}] OK : {sortie}")


def main() -> None:
    for annee in ANNEES:
        if annee not in RESSOURCES:
            raise SystemExit(f"Année {annee} absente de RESSOURCES : ajouter son identifiant et son sha1.")
        telecharger(annee)


if __name__ == "__main__":
    main()