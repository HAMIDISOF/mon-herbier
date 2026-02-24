# -*- coding: utf-8 -*-
"""
app.py — Serveur Flask de Mon Herbier
======================================
Routes :
  GET  /                          → liste des plantes (avec filtres)
  GET  /plante/<id>               → fiche détail
  GET  /plante/nouveau/<type>     → formulaire ajout
  GET  /plante/<id>/modifier      → formulaire modification
  POST /plante/sauvegarder        → enregistre ajout/modif
  POST /plante/<id>/supprimer     → supprime une plante
  GET  /journal                   → journal global
  GET  /journal/<plante_id>       → journal d'une plante
  POST /journal/ajouter           → ajoute une entrée
  POST /journal/<id>/supprimer    → supprime une entrée
  POST /importer                  → import des fiches .docx du dossier fiches/
  GET  /api/plantes               → API JSON (recherche)

Lancement :
  python app.py
  → http://localhost:5000
"""

from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from datetime import date
import os

from database import (
    init_db, lister_plantes, get_plante, sauvegarder_plante, supprimer_plante,
    get_journal, get_journal_global, ajouter_entree_journal, supprimer_entree_journal
)
from extract_fiches import importer_dossier
from models import creer_plante, TYPE_LABELS, TYPE_COULEURS, EntreeJournal

app = Flask(__name__)
app.secret_key = "herbier-secret-key-change-en-prod"

DOSSIER_FICHES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fiches")

# Crée le dossier fiches/ s'il n'existe pas
os.makedirs(DOSSIER_FICHES, exist_ok=True)


# ══════════════════════════════════════════════════════════════════════════════
# CONTEXT PROCESSORS (variables disponibles dans tous les templates)
# ══════════════════════════════════════════════════════════════════════════════

@app.context_processor
def inject_globals():
    return {
        "type_labels":   TYPE_LABELS,
        "type_couleurs": TYPE_COULEURS,
        "today":         date.today().isoformat(),
    }


# ══════════════════════════════════════════════════════════════════════════════
# LISTE PRINCIPALE
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/")
def index():
    type_filtre = request.args.get("type", "")
    recherche   = request.args.get("q", "")
    plantes = lister_plantes(
        type_filtre=type_filtre or None,
        recherche=recherche or None
    )
    return render_template("index.html",
                           plantes=plantes,
                           type_filtre=type_filtre,
                           recherche=recherche)


# ══════════════════════════════════════════════════════════════════════════════
# FICHE DÉTAIL
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/plante/<int:plante_id>")
def detail(plante_id):
    plante = get_plante(plante_id)
    if not plante:
        flash("Plante introuvable.", "error")
        return redirect(url_for("index"))
    journal = get_journal(plante_id)
    return render_template("detail.html", plante=plante, journal=journal)


# ══════════════════════════════════════════════════════════════════════════════
# FORMULAIRE AJOUT / MODIFICATION
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/plante/nouveau/<type_>")
def nouveau(type_):
    if type_ not in ("brute", "complement", "he", "jardin"):
        flash("Type inconnu.", "error")
        return redirect(url_for("index"))
    plante = creer_plante(type_)
    return render_template("formulaire.html", plante=plante, mode="ajout")


@app.route("/plante/<int:plante_id>/modifier")
def modifier(plante_id):
    plante = get_plante(plante_id)
    if not plante:
        flash("Plante introuvable.", "error")
        return redirect(url_for("index"))
    return render_template("formulaire.html", plante=plante, mode="modif")


@app.route("/plante/sauvegarder", methods=["POST"])
def sauvegarder():
    """Reçoit le formulaire (ajout ou modif) et sauvegarde en base."""
    form = request.form
    type_ = form.get("type_")
    plante_id = form.get("plante_id", "").strip()

    # Récupère l'objet existant ou en crée un nouveau
    if plante_id:
        obj = get_plante(int(plante_id))
        if not obj:
            flash("Plante introuvable.", "error")
            return redirect(url_for("index"))
    else:
        obj = creer_plante(type_)

    # Champs communs
    obj.nom          = form.get("nom", "").strip()
    obj.latin        = form.get("latin", "").strip()
    obj.famille      = form.get("famille", "").strip()
    obj.bio          = form.get("bio") == "on"
    obj.proprietes   = form.get("proprietes", "").strip()
    obj.contre       = form.get("contre", "").strip()
    obj.interactions = form.get("interactions", "").strip()
    obj.precautions  = form.get("precautions", "").strip()
    obj.distributeur = form.get("distributeur", "").strip()
    obj.prix         = form.get("prix", "").strip()
    obj.quantite     = form.get("quantite", "").strip()
    obj.stockage     = form.get("stockage", "").strip()
    obj.liens        = form.get("liens", "").strip()
    obj.notes        = form.get("notes", "").strip()

    # Champs spécifiques
    from database import CHAMPS_SPECIFIQUES
    for champ in CHAMPS_SPECIFIQUES.get(type_, []):
        if champ == "vivace":
            setattr(obj, champ, form.get(champ) == "on")
        else:
            setattr(obj, champ, form.get(champ, "").strip())

    if not obj.nom:
        flash("Le nom est obligatoire.", "error")
        return render_template("formulaire.html", plante=obj,
                               mode="modif" if plante_id else "ajout")

    new_id = sauvegarder_plante(obj)
    flash(f"✅ {obj.nom} enregistré(e) avec succès.", "success")
    return redirect(url_for("detail", plante_id=new_id))


# ══════════════════════════════════════════════════════════════════════════════
# SUPPRESSION
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/plante/<int:plante_id>/supprimer", methods=["POST"])
def supprimer(plante_id):
    plante = get_plante(plante_id)
    nom = plante.nom if plante else "?"
    supprimer_plante(plante_id)
    flash(f"🗑️ {nom} supprimé(e).", "info")
    return redirect(url_for("index"))


# ══════════════════════════════════════════════════════════════════════════════
# JOURNAL
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/journal")
def journal_global():
    entrees = get_journal_global()
    return render_template("journal.html", entrees=entrees, plante=None)


@app.route("/journal/<int:plante_id>")
def journal_plante(plante_id):
    plante = get_plante(plante_id)
    entrees = get_journal(plante_id)
    return render_template("journal.html", entrees=entrees, plante=plante)


@app.route("/journal/ajouter", methods=["POST"])
def journal_ajouter():
    form = request.form
    entree = EntreeJournal(
        plante_id=int(form["plante_id"]),
        date=form.get("date", date.today().isoformat()),
        action=form.get("action", "").strip(),
        notes=form.get("notes", "").strip(),
    )
    ajouter_entree_journal(entree)
    flash("📓 Entrée ajoutée au journal.", "success")
    return redirect(url_for("detail", plante_id=entree.plante_id))


@app.route("/journal/<int:entree_id>/supprimer", methods=["POST"])
def journal_supprimer(entree_id):
    plante_id = request.form.get("plante_id")
    supprimer_entree_journal(entree_id)
    flash("Entrée supprimée.", "info")
    return redirect(url_for("detail", plante_id=plante_id))


# ══════════════════════════════════════════════════════════════════════════════
# IMPORT FICHES .docx
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/importer", methods=["POST"])
def importer():
    """
    Scanne le dossier fiches/ et importe toutes les nouvelles fiches .docx.
    Les fiches déjà importées ne sont pas dédupliquées automatiquement
    (à améliorer avec un suivi des fichiers traités).
    """
    plantes_extraites, erreurs = importer_dossier(DOSSIER_FICHES)
    nb_ok = 0
    for p in plantes_extraites:
        try:
            sauvegarder_plante(p)
            nb_ok += 1
        except Exception as e:
            erreurs.append(f"{p.nom} ({e})")

    if nb_ok:
        flash(f"✅ {nb_ok} fiche(s) importée(s) avec succès.", "success")
    if erreurs:
        flash(f"⚠️ {len(erreurs)} erreur(s) : {', '.join(erreurs)}", "warning")
    if not nb_ok and not erreurs:
        flash("ℹ️ Aucune fiche .docx trouvée dans le dossier fiches/.", "info")

    return redirect(url_for("index"))


# ══════════════════════════════════════════════════════════════════════════════
# API JSON
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/api/plantes")
def api_plantes():
    """Retourne la liste des plantes au format JSON (pour usage futur)."""
    type_filtre = request.args.get("type")
    recherche   = request.args.get("q")
    plantes = lister_plantes(type_filtre=type_filtre, recherche=recherche)
    return jsonify([p.to_dict() for p in plantes])


# ══════════════════════════════════════════════════════════════════════════════
# LANCEMENT
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    init_db()
    print("🌿 Mon Herbier — http://localhost:5000")
    print("   Ctrl+C pour quitter")
    import threading, webbrowser
    threading.Timer(1.2, lambda: webbrowser.open("http://localhost:5000")).start()
    try:
        app.run(debug=True, port=5000)
    except KeyboardInterrupt:
        print("\n🌿 Au revoir !")

# ══════════════════════════════════════════════════════════════════════════════
# QUITTER
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/quitter", methods=["POST"])
def quitter():
    import threading, os, signal, time

    def _arreter():
        time.sleep(1)
        os.kill(os.getpid(), signal.SIGTERM)

    threading.Thread(target=_arreter, daemon=True).start()

    return """<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <title>Au revoir</title>
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400&display=swap" rel="stylesheet">
  <style>
    body { font-family:'Cormorant Garamond',serif; background:#f4efe6;
           display:flex; align-items:center; justify-content:center;
           height:100vh; margin:0; color:#2a2018; }
    h1 { font-size:2rem; font-weight:300; margin-bottom:.5rem; }
    p  { color:#7a6d58; }
  </style>
</head>
<body>
  <div style="text-align:center">
    <h1>🌿 À bientôt !</h1>
    <p>Mon Herbier s'est arrêté. Cette fenêtre va se fermer…</p>
  </div>
  <script>setTimeout(() => window.close(), 1200);</script>
</body>
</html>"""
