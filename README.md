# 🌿 Mon Herbier — v3.1

Application de gestion de plantes médicinales, compléments alimentaires et huiles essentielles.
**Stack** : Python · Flask · SQLite · HTML/JS

---

## 📁 Structure des fichiers

```
Herbier_app/
├── app.py              ← Serveur Flask (à lancer)
├── models.py           ← Classes Plante, Complement, HuileEssentielle, PlanteJardin
├── database.py         ← Couche SQLite (CRUD, tables, journal)
├── extract_fiches.py   ← Extraction automatique des fiches .docx
├── migrate.py          ← Migration depuis l'ancien herbier_data.json
├── requirements.txt    ← Dépendances Python
├── herbier.db          ← Base SQLite (créée au 1er lancement, non versionnée)
├── fiches/             ← Dossier de dépôt des fiches .docx à importer
│   └── MODELE_FICHE.txt ← Modèles de fiches pour les 4 types
└── templates/
    ├── base.html       ← Navigation, thème, flashs, bouton Quitter
    ├── index.html      ← Liste + recherche + filtres
    ├── detail.html     ← Fiche détail + journal de cure
    ├── formulaire.html ← Ajout / modification
    └── journal.html    ← Journal global
```

---

## 🚀 Installation & lancement

```bash
# 1. Installer les dépendances (une seule fois)
pip install -r requirements.txt

# 2. Lancer l'application
python app.py
# → Le navigateur s'ouvre automatiquement sur http://localhost:5000
```

Pour quitter : bouton **"✕ Quitter"** dans la navigation, ou **Ctrl+C** dans le terminal.

---

## 🔄 Migration depuis l'ancienne version (Tkinter / JSON)

Si tu as un fichier `herbier_data.json` issu de l'ancienne version Tkinter :

```bash
# 1. Place herbier_data.json dans le dossier Herbier_app/
# 2. Lance la migration (une seule fois)
python migrate.py
```

Le script détecte automatiquement les types, migre `maladies` → `proprietes`, conserve les liens Word locaux, et ne modifie pas le JSON original.

---

## 📂 Importer des fiches Word

1. Crée tes fiches `.docx` selon le format `fiches/MODELE_FICHE.txt`
2. Dépose-les dans le dossier `fiches/`
3. Clique sur **"📂 Importer fiches"** dans la navigation

Structure minimale :
```
Nom commun: Ortie
Type: plante brute
```

Labels insensibles à la casse. Champs inconnus ignorés silencieusement.

---

## 🏗️ Architecture

### Modèle objet (`models.py`)

```
Plante (base)
  ├── PlanteBrute      🌿  tisanes, décoctions, macérats
  ├── Complement       💊  gélules, comprimés, ampoules
  ├── HuileEssentielle 💧  huiles essentielles pures
  └── PlanteJardin     🌱  culture, semis, récolte
```

### Base de données (`database.py`)

- `plantes` — champs communs
- `plantes_brutes` / `complements` / `huiles_essentielles` / `plantes_jardin` — champs spécifiques
- `journal` — journal de cure (lié par `plante_id`)

> ⚠️ `CHAMPS_SPECIFIQUES` est dans `database.py`, pas dans `models.py`

### Routes Flask (`app.py`)

| Méthode | Route | Action |
|---------|-------|--------|
| GET | `/` | Liste avec filtres et recherche |
| GET | `/plante/<id>` | Fiche détail + journal |
| GET | `/plante/nouveau/<type>` | Formulaire ajout |
| GET | `/plante/<id>/modifier` | Formulaire modification |
| POST | `/plante/sauvegarder` | Enregistre ajout/modif |
| POST | `/plante/<id>/supprimer` | Supprime une plante |
| GET | `/journal` | Journal global |
| POST | `/journal/ajouter` | Ajoute une entrée journal |
| POST | `/journal/<id>/supprimer` | Supprime une entrée journal |
| POST | `/importer` | Import fiches .docx |
| POST | `/quitter` | Arrête Flask + ferme l'onglet |
| GET | `/api/plantes` | API JSON |

---

## ⚠️ Points d'attention connus

**Import correct de CHAMPS_SPECIFIQUES :**
```python
# ❌  from models import CHAMPS_SPECIFIQUES
# ✅  from database import CHAMPS_SPECIFIQUES
```

**Fermeture onglet :** `window.close()` peut être bloqué par le navigateur. Flask s'arrête bien dans tous les cas, mais l'onglet peut rester ouvert — fermer manuellement si besoin.

**Double ouverture navigateur :** le mode `debug=True` redémarre Flask à chaque modif de code, ce qui peut rouvrir le navigateur. Comportement normal du reloader.

**Serveur de dev :** le `WARNING: This is a development server` est normal pour un usage local.

---

## ➕ Ajouter un nouveau type (ex: PlanteJardin était prévu en mars 2026)

1. `models.py` — créer la classe + ajouter dans `TYPE_LABELS`, `TYPE_COULEURS`, `CLASSES_MAP`
2. `database.py` — créer la table + ajouter dans `TABLE_SPECIFIQUE` et `CHAMPS_SPECIFIQUES`
3. `templates/formulaire.html` — ajouter le bloc de champs
4. `templates/detail.html` — ajouter la vue détail
5. `templates/base.html` — ajouter l'option dans le dropdown "+ Ajouter"

---

## 🔁 Workflow Git

```bash
# Modifications courantes
git add .
git commit -m "description"
git push

# Premier push seulement
git init
git remote add origin https://github.com/HAMIDISOF/mon-herbier.git
git push -u origin main --force
```

> `git remote add` → une seule fois. Si `error: remote origin already exists` → sauter cette ligne.

---

## 📅 Évolutions prévues

- [ ] Alertes stock faible
- [ ] Export PDF des fiches
- [ ] Impression de fiches
- [ ] Gestion de la bibliothèque (livres de référence)
- [ ] Statistiques de consommation
- [ ] Déduplication à l'import (éviter les doublons)

---

## 🎨 Thème visuel

Typographie : **Cormorant Garamond** (titres) + **DM Sans** (corps). Palette tons naturels.

| Variable CSS | Couleur | Usage |
|---|---|---|
| `--bg` | Beige clair | Fond général |
| `--paper` | Blanc cassé | Cards, formulaires |
| `--vert` / `--vert2` | Vert foncé | Plantes brutes, actions |
| `--brun` | Brun | Précautions |
| `--rouge` | Rouge brique | Contre-indications, suppression |
| `--bleu` | Bleu-gris | Compléments |
| `--olive` | Vert olive | Plantes jardin |

---

*Dernière mise à jour : février 2026 — v3.1*
