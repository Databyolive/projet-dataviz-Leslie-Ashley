"""Illustrations vectorielles (SVG) dessinées pour le projet : libres de droits, aucune image externe.

Chaque fonction renvoie une chaîne SVG ; `en_image()` la transforme en balise <img> (data URI) pour l'afficher dans Streamlit.
"""
import base64


def en_image(svg: str, largeur: str = "100%", alt: str = "", classe: str = "") -> str:
    b64 = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f'<img class="{classe}" alt="{alt}" style="width:{largeur};height:auto;display:block" src="data:image/svg+xml;base64,{b64}"/>'


def _fenetres(x, y, w, h, colonnes, lignes, marge=7, couleur="#FFE9A8"):
    cases = []
    lw = (w - marge * (colonnes + 1)) / colonnes
    lh = (h - marge * (lignes + 1)) / lignes
    for i in range(lignes):
        for j in range(colonnes):
            fx = x + marge + j * (lw + marge)
            fy = y + marge + i * (lh + marge)
            cases.append(f'<rect x="{fx:.1f}" y="{fy:.1f}" width="{lw:.1f}" height="{lh:.1f}" rx="1.5" fill="{couleur}"/>')
    return "".join(cases)


def _maison(x, base, w, h, mur, toit, porte="#0B2545"):
    hauteur_toit = h * 0.45
    return (f'<rect x="{x}" y="{base - h}" width="{w}" height="{h}" fill="{mur}"/>'
            f'<polygon points="{x - 5},{base - h} {x + w / 2},{base - h - hauteur_toit} {x + w + 5},{base - h}" fill="{toit}"/>'
            f'<rect x="{x + w * 0.72}" y="{base - h - hauteur_toit * 0.8}" width="7" height="{hauteur_toit * 0.6}" fill="{toit}"/>'
            f'<rect x="{x + w * 0.4}" y="{base - h * 0.52}" width="{w * 0.2}" height="{h * 0.52}" fill="{porte}"/>'
            f'<rect x="{x + w * 0.12}" y="{base - h * 0.75}" width="{w * 0.2}" height="{h * 0.28}" rx="1.5" fill="#FFE9A8"/>'
            f'<rect x="{x + w * 0.68}" y="{base - h * 0.75}" width="{w * 0.2}" height="{h * 0.28}" rx="1.5" fill="#FFE9A8"/>')


def _arbre(x, base, r=14):
    return (f'<rect x="{x - 2}" y="{base - r}" width="4" height="{r}" fill="#6B4F3A"/>'
            f'<circle cx="{x}" cy="{base - r - r * 0.7}" r="{r}" fill="#2E8B6E"/><circle cx="{x - r * 0.5}" cy="{base - r - r * 0.2}" r="{r * 0.7}" fill="#3AA683"/>')


def bandeau() -> str:
    """Grand bandeau : lever de soleil sur un quartier de maisons et d'immeubles."""
    base = 232
    elements = [
        '<defs>'
        '<linearGradient id="ciel" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#16325C"/><stop offset="0.55" stop-color="#E86A5D"/><stop offset="1" stop-color="#FFC878"/></linearGradient>'
        '<linearGradient id="colline" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2F6F73"/><stop offset="1" stop-color="#1F4E57"/></linearGradient>'
        '</defs>',
        '<rect width="640" height="260" fill="url(#ciel)"/>',
        '<circle cx="470" cy="150" r="58" fill="#FFE9A8" opacity="0.35"/><circle cx="470" cy="150" r="38" fill="#FFF3C9"/>',
        '<ellipse cx="120" cy="54" rx="42" ry="9" fill="#fff" opacity="0.18"/><ellipse cx="170" cy="66" rx="30" ry="7" fill="#fff" opacity="0.14"/>',
        '<ellipse cx="540" cy="40" rx="36" ry="8" fill="#fff" opacity="0.16"/>',
        '<path d="M0 205 C 90 150 180 190 270 170 C 360 150 450 200 640 160 L640 260 L0 260 Z" fill="url(#colline)"/>',
        # immeuble haussmannien
        '<rect x="40" y="96" width="112" height="136" fill="#F2E3C6"/>',
        '<polygon points="34,96 158,96 146,64 46,64" fill="#3B4A6B"/>',
        '<rect x="62" y="70" width="14" height="22" fill="#2B3754"/><rect x="112" y="70" width="14" height="22" fill="#2B3754"/>',
        _fenetres(40, 100, 112, 128, 4, 4, 8, "#7FA8C9"),
        '<rect x="40" y="184" width="112" height="4" fill="#D7C39B"/>',
        # tour d'appartements
        '<rect x="176" y="70" width="74" height="162" fill="#C9D4E5"/>',
        _fenetres(176, 74, 74, 154, 3, 7, 6, "#FFE9A8"),
        '<rect x="170" y="64" width="86" height="8" fill="#8EA2C4"/>',
        # maisons
        _maison(276, base, 66, 52, "#F7E1C2", "#C8553D"),
        _maison(356, base, 58, 44, "#E7EEF8", "#3B4A6B"),
        _maison(540, base, 70, 56, "#F9D9C9", "#8A3B2E"),
        # petit collectif
        '<rect x="424" y="146" width="92" height="86" fill="#E9C4A0"/><polygon points="418,146 470,120 522,146" fill="#6E3B2A"/>',
        _fenetres(424, 150, 92, 78, 4, 3, 7, "#FFF3C9"),
        _arbre(268, base + 2, 11), _arbre(418, base + 2, 10), _arbre(526, base + 2, 12), _arbre(18, base + 2, 13),
        # panneau « à vendre »
        '<rect x="602" y="196" width="3" height="40" fill="#5B3B2B"/><rect x="580" y="186" width="48" height="22" rx="3" fill="#FFFFFF"/>'
        '<text x="604" y="201" font-family="Arial, sans-serif" font-size="10" font-weight="700" text-anchor="middle" fill="#C8553D">À VENDRE</text>',
        '<rect y="232" width="640" height="28" fill="#183B45"/>',
    ]
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 260" role="img" aria-label="Illustration d\'un quartier de maisons et d\'immeubles au lever du soleil">' + "".join(elements) + "</svg>"


def _icone(contenu: str, fond: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><circle cx="32" cy="32" r="30" fill="{fond}"/>{contenu}</svg>')


ICONES = {
    "ventes": lambda: _icone(
        '<polygon points="14,31 32,15 50,31" fill="#fff"/><rect x="19" y="30" width="26" height="19" fill="#fff"/>'
        '<rect x="29" y="38" width="7" height="11" fill="#1B6CA8"/><rect x="40" y="33" width="9" height="3" rx="1" fill="#1B6CA8" opacity="0"/>'
        '<path d="M44 14 l4 4 -4 4" stroke="#fff" stroke-width="3" fill="none" stroke-linecap="round"/>', "#1B6CA8"),
    "prix_m2": lambda: _icone(
        '<rect x="14" y="16" width="36" height="32" rx="4" fill="none" stroke="#fff" stroke-width="3"/>'
        '<path d="M14 28 h36 M30 16 v32" stroke="#fff" stroke-width="2" opacity="0.55"/>'
        '<text x="32" y="41" font-family="Arial, sans-serif" font-size="15" font-weight="700" text-anchor="middle" fill="#fff">€</text>', "#D1495B"),
    "ecart": lambda: _icone(
        '<path d="M32 14 v36" stroke="#fff" stroke-width="3"/><path d="M16 22 h32" stroke="#fff" stroke-width="3" stroke-linecap="round"/>'
        '<path d="M16 22 l-6 14 h12 z M48 22 l-6 14 h12 z" fill="#fff"/><rect x="22" y="48" width="20" height="4" rx="2" fill="#fff"/>', "#13A89E"),
    "prix_median": lambda: _icone(
        '<path d="M18 18 h20 l10 10 -18 18 -12 -12 z" fill="#fff"/><circle cx="26" cy="26" r="3" fill="#F4A259"/>'
        '<text x="35" y="38" font-family="Arial, sans-serif" font-size="10" font-weight="700" fill="#F4A259" transform="rotate(45 35 38)">€</text>', "#F4A259"),
    "evolution": lambda: _icone(
        '<polyline points="14,44 26,32 34,38 50,20" fill="none" stroke="#fff" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>'
        '<polyline points="42,20 50,20 50,28" fill="none" stroke="#fff" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>', "#6C5CE7"),
    "contexte": lambda: _icone(
        '<circle cx="32" cy="32" r="16" fill="none" stroke="#fff" stroke-width="3"/><path d="M16 32 h32 M32 16 c-9 9 -9 23 0 32 M32 16 c9 9 9 23 0 32" stroke="#fff" stroke-width="2.5" fill="none"/>', "#1B6CA8"),
    "constat": lambda: _icone(
        '<circle cx="28" cy="28" r="12" fill="none" stroke="#fff" stroke-width="4"/><path d="M37 37 l13 13" stroke="#fff" stroke-width="5" stroke-linecap="round"/>', "#D1495B"),
    "recommandation": lambda: _icone(
        '<path d="M32 12 c-9 0 -15 7 -15 15 c0 11 15 25 15 25 s15 -14 15 -25 c0 -8 -6 -15 -15 -15 z" fill="#fff"/><circle cx="32" cy="27" r="6" fill="#13A89E"/>', "#13A89E"),
}


def icone(nom: str, taille: int = 56) -> str:
    return en_image(ICONES[nom](), largeur=f"{taille}px", alt=nom)
