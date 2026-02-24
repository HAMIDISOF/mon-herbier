# -*- coding: utf-8 -*-
"""
extract_fiches.py — Extraction de fiches Word structurées
==========================================================
Lit un fichier .docx structuré avec des balises de la forme :
  Nom commun: Ortie
  Type: plante brute
  Propriétés: Diurétique, reminéralisant...

Retourne un objet Plante du bon type, prêt à être sauvegardé via database.py.

Structure attendue des fiches Word :
  - Chaque champ sur sa propre ligne : "Label: valeur"
  - Les champs multilignes se terminent quand un nouveau label est reconnu
  - La casse des labels est ignorée (nom commun = Nom commun = NOM COMMUN)
  - Les champs inconnus sont ignorés silencieusement

Usage :
  from extract_fiches import extraire_fiche, importer_dossier
  plante = extraire_fiche("fiches/Ortie.docx")
  if plante:
      sauvegarder_plante(plante)
"""

import os
import re
from docx import Document
from models import creer_plante, Plante
from database import CHAMPS_SPECIFIQUES

# ══════════════════════════════════════════════════════════════════════════════
# MAPPING LABELS → ATTRIBUTS
# ══════════════════════════════════════════════════════════════════════════════
# Clé   = label tel qu'il apparaît dans la fiche (insensible à la casse)
# Valeur = nom de l'attribut Python dans les classes

LABELS_COMMUNS = {
    "nom commun":                "nom",
    "nom":                       "nom",
    "nom scientifique":          "latin",
    "latin":                     "latin",
    "famille botanique":         "famille",
    "famille":                   "famille",
    "biologique":                "bio",
    "bio":                       "bio",
    "propriétés":                "proprietes",
    "proprietes":                "proprietes",
    "indications":               "proprietes",
    "bénéfices":                 "proprietes",
    "contre-indications":        "contre",
    "contre indications":        "contre",
    "interactions médicamenteuses": "interactions",
    "interactions":              "interactions",
    "précautions":               "precautions",
    "precautions":               "precautions",
    "distributeur":              "distributeur",
    "fournisseur":               "distributeur",
    "prix":                      "prix",
    "quantité en stock":         "quantite",
    "quantité":                  "quantite",
    "stock":                     "quantite",
    "lieu de stockage":          "stockage",
    "stockage":                  "stockage",
    "liens":                     "liens",
    "liens ressources":          "liens",
    "ressources":                "liens",
    "notes":                     "notes",
}

LABELS_BRUTE = {
    "partie utilisée":    "partie",
    "partie":             "partie",
    "origine":            "origine",
    "provenance":         "origine",
    "mode de préparation":"mode_preparation",
    "préparation":        "mode_preparation",
    "température":        "temperature",
    "temps d'infusion":   "temps_infusion",
    "infusion":           "temps_infusion",
    "posologie":          "posologie",
    "conditionnement":    "conditionnement",
}

LABELS_COMPLEMENT = {
    "partie utilisée":    "partie",
    "partie":             "partie",
    "origine":            "origine",
    "référence produit":  "reference",
    "référence":          "reference",
    "forme":              "forme",
    "dosage":             "dosage",
    "posologie":          "posologie",
    "moment de prise":    "moment_prise",
    "moment":             "moment_prise",
    "durée de cure":      "duree_cure",
    "durée":              "duree_cure",
    "conditionnement":    "conditionnement",
}

LABELS_HE = {
    "organe distillé":    "organe",
    "organe":             "organe",
    "origine":            "origine",
    "mode d'obtention":   "mode_obtention",
    "obtention":          "mode_obtention",
    "chémotype":          "chemotype",
    "chemotype":          "chemotype",
    "composition":        "composition",
    "voies d'utilisation":"voies",
    "voies":              "voies",
    "précautions par voie":"precautions_voies",
    "précautions voies":  "precautions_voies",
    "date limite":        "dlc",
    "dlc":                "dlc",
}

LABELS_JARDIN = {
    "partie":             "partie",
    "emplacement":        "emplacement",
    "exposition":         "exposition",
    "type de sol":        "type_sol",
    "sol":                "type_sol",
    "période de semis":   "periode_semis",
    "semis":              "periode_semis",
    "période de récolte": "periode_recolte",
    "récolte":            "periode_recolte",
    "vivace":             "vivace",
    "hivernage":          "hivernage",
    "entretien":          "entretien",
}

TYPE_MAP_LABELS = {
    "brute":      {**LABELS_COMMUNS, **LABELS_BRUTE},
    "complement": {**LABELS_COMMUNS, **LABELS_COMPLEMENT},
    "he":         {**LABELS_COMMUNS, **LABELS_HE},
    "jardin":     {**LABELS_COMMUNS, **LABELS_JARDIN},
}

# Synonymes pour le champ "type" dans la fiche
TYPE_SYNONYMES = {
    "plante brute":        "brute",
    "brute":               "brute",
    "tisane":              "brute",
    "complément":          "complement",
    "complement":          "complement",
    "compléments":         "complement",
    "huile essentielle":   "he",
    "he":                  "he",
    "huile":               "he",
    "jardin":              "jardin",
    "plante jardin":       "jardin",
    "jardin potager":      "jardin",
}


# ══════════════════════════════════════════════════════════════════════════════
# EXTRACTION
# ══════════════════════════════════════════════════════════════════════════════

def _normaliser_label(texte: str) -> str:
    """Normalise un label pour la comparaison (minuscules, sans accents doublés)."""
    return texte.strip().lower().rstrip(":")


def _valeur_bool(texte: str) -> bool:
    """Interprète 'oui/non/true/false/1/0' en booléen."""
    return texte.strip().lower() in ("oui", "yes", "true", "1", "vrai")


def extraire_fiche(fichier_path: str) -> Plante | None:
    """
    Lit un fichier .docx structuré et retourne un objet Plante.

    Retourne None si :
      - le fichier n'existe pas
      - le champ 'nom commun' est absent
      - le champ 'type' est absent ou non reconnu

    Affiche des warnings pour les champs non reconnus.
    """
    if not os.path.exists(fichier_path):
        print(f"❌ Fichier introuvable : {fichier_path}")
        return None

    try:
        doc = Document(fichier_path)
    except Exception as e:
        print(f"❌ Impossible de lire {fichier_path} : {e}")
        return None

    # ── Première passe : détecter le type ──────────────────────────────────
    type_detecte = None
    for para in doc.paragraphs:
        texte = para.text.strip()
        if not texte or ":" not in texte:
            continue
        label, _, valeur = texte.partition(":")
        if _normaliser_label(label) == "type":
            type_detecte = TYPE_SYNONYMES.get(valeur.strip().lower())
            if type_detecte:
                break

    if not type_detecte:
        print(f"⚠️  Type non reconnu dans {os.path.basename(fichier_path)}")
        return None

    # ── Deuxième passe : extraire tous les champs ──────────────────────────
    labels_map = TYPE_MAP_LABELS[type_detecte]
    donnees: dict[str, str] = {}
    champ_courant: str | None = None
    valeur_courante: list[str] = []

    def _sauver_champ():
        if champ_courant:
            donnees[champ_courant] = "\n".join(valeur_courante).strip()

    for para in doc.paragraphs:
        texte = para.text.strip()
        if not texte:
            if champ_courant:
                valeur_courante.append("")
            continue

        if ":" in texte:
            label_brut, _, valeur = texte.partition(":")
            label_norm = _normaliser_label(label_brut)
            attribut = labels_map.get(label_norm)

            if attribut:
                _sauver_champ()
                champ_courant = attribut
                valeur_courante = [valeur.strip()]
                continue
            # Pas un label reconnu → continuation du champ courant
        if champ_courant:
            valeur_courante.append(texte)

    _sauver_champ()  # sauver le dernier champ

    # ── Validation ────────────────────────────────────────────────────────
    nom = donnees.get("nom", "").strip()
    if not nom:
        print(f"⚠️  Champ 'Nom commun' manquant dans {os.path.basename(fichier_path)}")
        return None

    # ── Construction de l'objet ───────────────────────────────────────────
    obj = creer_plante(type_detecte)
    for attribut, valeur in donnees.items():
        if not hasattr(obj, attribut):
            continue
        if attribut in ("bio", "vivace"):
            setattr(obj, attribut, _valeur_bool(valeur))
        else:
            setattr(obj, attribut, valeur)

    print(f"✅ Fiche extraite : {nom} ({type_detecte})")
    return obj


# ══════════════════════════════════════════════════════════════════════════════
# IMPORT EN LOT
# ══════════════════════════════════════════════════════════════════════════════

def importer_dossier(dossier: str) -> tuple[list[Plante], list[str]]:
    """
    Parcourt un dossier et extrait toutes les fiches .docx.

    Retourne :
      - liste des objets Plante extraits avec succès
      - liste des noms de fichiers en erreur

    Usage dans app.py :
      from extract_fiches import importer_dossier
      from database import sauvegarder_plante
      plantes, erreurs = importer_dossier("fiches")
      for p in plantes:
          sauvegarder_plante(p)
    """
    if not os.path.isdir(dossier):
        print(f"❌ Dossier introuvable : {dossier}")
        return [], [dossier]

    succes = []
    erreurs = []

    fichiers = [f for f in os.listdir(dossier) if f.lower().endswith(".docx")
                and not f.startswith("~")]  # ignore les fichiers Word ouverts

    if not fichiers:
        print(f"ℹ️  Aucun fichier .docx trouvé dans {dossier}")
        return [], []

    for fichier in sorted(fichiers):
        chemin = os.path.join(dossier, fichier)
        plante = extraire_fiche(chemin)
        if plante:
            succes.append(plante)
        else:
            erreurs.append(fichier)

    print(f"\n📊 Import terminé : {len(succes)} succès, {len(erreurs)} erreurs")
    return succes, erreurs
