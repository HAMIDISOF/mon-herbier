# -*- coding: utf-8 -*-
"""
migrate.py — Migration herbier_data.json → herbier.db
======================================================
À lancer UNE SEULE FOIS depuis le dossier Herbier_app/ :

  python migrate.py

Ce script :
  1. Lit herbier_data.json (ancien format)
  2. Convertit chaque entrée en objet Python (nouveau modèle)
  3. Insère dans herbier.db via database.py
  4. Affiche un rapport de migration

Correspondances de champs :
  ancien "maladies"  → nouveau "proprietes"
  ancien "lien"      → nouveau "liens"  (chemin local conservé)
  ancien "_type"     → déduit du champ "partie" si possible, sinon "brute" par défaut
  ancien "id"        → ignoré (nouvel id auto-incrémenté SQLite)
"""

import json
import os
import sys

# ── S'assure qu'on peut importer les modules du projet ────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import creer_plante
from database import init_db, sauvegarder_plante

JSON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "herbier_data.json")


def deviner_type(entree: dict) -> str:
    """
    Tente de deviner le type d'entrée à partir des données disponibles.
    Logique :
      - Si _type est présent (nouvelles versions) → on l'utilise directement
      - Si "partie" contient "huile essentielle" ou "HE" → "he"
      - Sinon → "brute" par défaut (le plus courant)
    """
    # Nouvelle version avec _type explicite
    if "_type" in entree:
        return entree["_type"]

    partie = entree.get("partie", "").lower()
    if "huile" in partie or " he" in partie or partie == "he":
        return "he"
    if "gélule" in partie or "comprimé" in partie or "complément" in partie:
        return "complement"

    return "brute"  # défaut


def migrer_entree(entree: dict) -> tuple:
    """
    Convertit un dictionnaire JSON (ancien format) en objet Plante.
    Retourne (objet, avertissements).
    """
    avertissements = []
    type_ = deviner_type(entree)
    obj = creer_plante(type_)

    # ── Champs directs ────────────────────────────────────────────────────────
    obj.nom          = entree.get("nom", "").strip()
    obj.latin        = entree.get("latin", "").strip()
    obj.contre       = entree.get("contre", "").strip()
    obj.precautions  = entree.get("precautions", "").strip()
    obj.distributeur = entree.get("distributeur", "").strip()
    obj.prix         = entree.get("prix", "").strip()
    obj.quantite     = entree.get("quantite", "").strip()
    obj.stockage     = entree.get("stockage", "").strip()
    obj.notes        = entree.get("notes", "").strip()
    obj.bio          = bool(entree.get("bio", False))

    # ── Mapping ancien → nouveau ──────────────────────────────────────────────
    # "maladies" → "proprietes"
    maladies = entree.get("maladies", "").strip()
    proprietes = entree.get("proprietes", "").strip()
    obj.proprietes = proprietes or maladies
    if maladies and not proprietes:
        avertissements.append(f"  → champ 'maladies' migré vers 'proprietes'")

    # "lien" → "liens" (conserve le chemin local, préfixé pour clarté)
    lien = entree.get("lien", "").strip()
    if lien:
        obj.liens = f"Fiche Word: {lien}"
        avertissements.append(f"  → lien local conservé dans 'liens'")

    # "partie" → attribut spécifique selon le type
    partie = entree.get("partie", "").strip()
    if partie and hasattr(obj, "partie"):
        # Pour HE, "partie" dans l'ancien format = organe distillé souvent
        if type_ == "he" and hasattr(obj, "organe") and not hasattr(obj, "partie"):
            obj.organe = partie
        else:
            obj.partie = partie

    # Famille botanique si présente
    if entree.get("famille"):
        obj.famille = entree["famille"].strip()

    # Interactions si présentes (nouvelle version)
    if entree.get("interactions"):
        obj.interactions = entree["interactions"].strip()

    return obj, avertissements


def migrer():
    """Lance la migration complète."""
    if not os.path.exists(JSON_PATH):
        print(f"❌ Fichier introuvable : {JSON_PATH}")
        print("   Place herbier_data.json dans le même dossier que migrate.py")
        return

    print("🌿 Migration herbier_data.json → herbier.db")
    print("=" * 50)

    # Charge le JSON
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        try:
            donnees = json.load(f)
        except json.JSONDecodeError as e:
            print(f"❌ Erreur de lecture JSON : {e}")
            return

    if not isinstance(donnees, list):
        print("❌ Format inattendu : le JSON doit être une liste.")
        return

    print(f"📄 {len(donnees)} entrée(s) trouvée(s) dans le JSON\n")

    # Initialise la base
    init_db()

    succes = []
    erreurs = []

    for i, entree in enumerate(donnees, 1):
        nom = entree.get("nom", f"[entrée {i}]")
        try:
            obj, avertissements = migrer_entree(entree)

            if not obj.nom:
                erreurs.append((nom, "Nom vide — entrée ignorée"))
                continue

            new_id = sauvegarder_plante(obj)
            type_label = {"brute": "🌿 Plante brute", "complement": "💊 Complément",
                          "he": "💧 HE", "jardin": "🌱 Jardin"}.get(obj.TYPE, obj.TYPE)
            print(f"  ✅ [{i}] {obj.nom} → {type_label} (id={new_id})")
            for avert in avertissements:
                print(f"     ⚠  {avert}")
            succes.append(obj.nom)

        except Exception as e:
            erreurs.append((nom, str(e)))
            print(f"  ❌ [{i}] {nom} → Erreur : {e}")

    # Rapport final
    print("\n" + "=" * 50)
    print(f"✅ Migration terminée : {len(succes)} succès, {len(erreurs)} erreur(s)")
    if erreurs:
        print("\nEntrées en erreur :")
        for nom, msg in erreurs:
            print(f"  ✗ {nom} : {msg}")

    print("\n💡 Tu peux maintenant compléter les fiches dans l'app :")
    print("   python app.py  →  http://localhost:5000")
    print("\n⚠️  Le fichier herbier_data.json n'a pas été modifié (conservation de l'original).")


if __name__ == "__main__":
    migrer()
