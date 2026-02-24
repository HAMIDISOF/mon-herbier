# -*- coding: utf-8 -*-
"""
models.py — Modèle objet de Mon Herbier
========================================
Hiérarchie des classes :
  Plante (base)
    ├── PlanteBrute
    ├── Complement
    ├── HuileEssentielle
    └── PlanteJardin

Chaque classe correspond à une table SQLite et à un type de fiche Word.
"""

from dataclasses import dataclass, field
from typing import Optional


# ══════════════════════════════════════════════════════════════════════════════
# CLASSE DE BASE
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class Plante:
    """
    Classe de base — attributs communs à tous les types.
    Ne pas instancier directement.
    """
    TYPE: str = field(default="base", init=False)

    id:           Optional[int] = None
    nom:          str  = ""          # Nom commun — OBLIGATOIRE
    latin:        str  = ""          # Nom scientifique
    famille:      str  = ""          # Famille botanique
    bio:          bool = False       # Agriculture biologique ?
    proprietes:   str  = ""          # Indications / bénéfices
    contre:       str  = ""          # Contre-indications
    interactions: str  = ""          # Interactions médicamenteuses ← nouveau
    precautions:  str  = ""          # Précautions générales
    distributeur: str  = ""          # Fournisseur habituel
    prix:         str  = ""          # Prix habituel
    quantite:     str  = ""          # Stock disponible
    stockage:     str  = ""          # Lieu de stockage
    liens:        str  = ""          # Ressources en ligne (label:url, ...)
    notes:        str  = ""          # Notes personnelles

    def to_dict(self) -> dict:
        """Sérialise l'objet en dictionnaire (pour l'API JSON)."""
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}


# ══════════════════════════════════════════════════════════════════════════════
# SOUS-CLASSES
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class PlanteBrute(Plante):
    """
    Plante utilisée sous forme brute : tisane, décoction, macérat, teinture...
    Couleur d'accent : vert (#4a7a35)
    """
    TYPE: str = field(default="brute", init=False)

    partie:           str = ""   # Partie de la plante utilisée
    origine:          str = ""   # Provenance géographique
    mode_preparation: str = ""   # Infusion, décoction, macérat...
    temperature:      str = ""   # Température de préparation
    temps_infusion:   str = ""   # Durée d'infusion / décoction
    posologie:        str = ""   # Dose recommandée
    conditionnement:  str = ""   # Vrac, sachets, bocal...


@dataclass
class Complement(Plante):
    """
    Complément alimentaire sous forme de produit fini.
    Exemples : Ginkgo en gélules, Curcuma en comprimés, Shilajit...
    Couleur d'accent : bleu-gris (#5b7fa6)
    """
    TYPE: str = field(default="complement", init=False)

    partie:          str = ""   # Partie de la plante utilisée
    origine:         str = ""   # Provenance géographique
    reference:       str = ""   # Référence produit
    forme:           str = ""   # Gélules, comprimés, ampoules...
    dosage:          str = ""   # Dosage par unité (ex: 405 mg)
    posologie:       str = ""   # Nombre d'unités par jour
    moment_prise:    str = ""   # Matin / midi / soir / repas
    duree_cure:      str = ""   # Durée conseillée (ex: 3 mois)
    conditionnement: str = ""   # Boîte 90 gélules, flacon...


@dataclass
class HuileEssentielle(Plante):
    """
    Huile essentielle pure (non mélangée).
    Exemples : Ravintsara, Lavande vraie, Tea Tree, Eucalyptus...
    Couleur d'accent : brun-orangé (#a0622a)
    """
    TYPE: str = field(default="he", init=False)

    organe:             str = ""   # Partie distillée (feuilles, fleurs...)
    origine:            str = ""   # Pays / région de production
    mode_obtention:     str = ""   # Distillation, expression à froid...
    chemotype:          str = ""   # Chémotype (CT)
    composition:        str = ""   # Composants principaux et %
    voies:              str = ""   # Voies d'utilisation
    precautions_voies:  str = ""   # Précautions détaillées par voie
    dlc:                str = ""   # Date limite de consommation


@dataclass
class PlanteJardin(Plante):
    """
    Plante cultivée au jardin ou en pot.
    Permet de suivre la culture, les périodes de semis et récolte.
    Couleur d'accent : vert olive (#6a8a4a)
    """
    TYPE: str = field(default="jardin", init=False)

    partie:          str  = ""    # Partie utilisée / récoltée
    emplacement:     str  = ""    # Jardin, balcon, serre...
    exposition:      str  = ""    # Plein soleil, mi-ombre, ombre
    type_sol:        str  = ""    # Argileux, sableux, limoneux...
    periode_semis:   str  = ""    # Ex: mars-avril
    periode_recolte: str  = ""    # Ex: juin-septembre ← nouveau
    vivace:          bool = False # Plante vivace ou annuelle ?
    hivernage:       str  = ""    # Instructions d'hivernage
    entretien:       str  = ""    # Arrosage, taille, fertilisation...


# ══════════════════════════════════════════════════════════════════════════════
# JOURNAL DE CURE
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class EntreeJournal:
    """
    Entrée du journal de cure pour une plante / complément / HE.
    Liée à une plante via plante_id.
    """
    id:        Optional[int] = None
    plante_id: int  = 0
    date:      str  = ""   # Format YYYY-MM-DD
    action:    str  = ""   # début cure, fin cure, observation, achat...
    notes:     str  = ""   # Notes libres


# ══════════════════════════════════════════════════════════════════════════════
# CONSTANTES D'INTERFACE
# ══════════════════════════════════════════════════════════════════════════════

TYPE_LABELS = {
    "brute":      "🌿 Plante brute",
    "complement": "💊 Complément",
    "he":         "💧 Huile essentielle",
    "jardin":     "🌱 Jardin",
}

TYPE_COULEURS = {
    "brute":      "#4a7a35",
    "complement": "#5b7fa6",
    "he":         "#a0622a",
    "jardin":     "#6a8a4a",
}

CLASSES_MAP = {
    "brute":      PlanteBrute,
    "complement": Complement,
    "he":         HuileEssentielle,
    "jardin":     PlanteJardin,
}

def creer_plante(type_: str) -> Plante:
    """
    Factory : crée une instance du bon type selon la chaîne passée.
    Ex: creer_plante("he") → HuileEssentielle()
    """
    cls = CLASSES_MAP.get(type_)
    if cls is None:
        raise ValueError(f"Type inconnu : {type_!r}. Valeurs valides : {list(CLASSES_MAP)}")
    return cls()
