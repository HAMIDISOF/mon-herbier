# 🌿 Mon Herbier — v4.0

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
│   ├── MODELE_FICHE.txt            ← Format texte de référence
│   ├── MODELE_complement.docx      ← Modèle Word — Complément alimentaire
│   ├── MODELE_plante_brute.docx    ← Modèle Word — Plante brute
│   ├── MODELE_huile_essentielle.docx ← Modèle Word — Huile essentielle
│   └── MODELE_plante_jardin.docx   ← Modèle Word — Plante de jardin
└── templates/
    ├── base.html       ← Navigation, thème, responsive mobile, bouton Quitter
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
# → Accessible depuis le réseau WiFi : http://<IP_DE_TON_PC>:5000
```

Pour quitter : bouton **"✕ Quitter"** dans la navigation, ou **Ctrl+C** dans le terminal.

---

## 📱 Accès depuis le téléphone (réseau WiFi local)

L'app est accessible depuis n'importe quel appareil connecté au même réseau WiFi.

1. Lance `python app.py` sur ton PC
2. Trouve l'IP de ton PC : ouvre un terminal → `ipconfig` → note l'**Adresse IPv4** (ex: `192.168.1.42`)
3. Sur ton téléphone → navigateur → `http://192.168.1.42:5000`

> L'interface est responsive : elle s'adapte automatiquement aux petits écrans (téléphone, tablette).

---

## 🔄 Migration depuis l'ancienne version (Tkinter / JSON)

Si tu as un fichier `herbier_data.json` issu de l'ancienne version Tkinter :

```bash
# 1. Place herbier_data.json dans le dossier Herbier_app/
# 2. Lance la migration (une seule fois)
python migrate.py
```

Le script :
- détecte automatiquement les types (`brute` / `complement` / `he`) selon le champ `partie`
- migre `maladies` (ancien) → `proprietes` (nouveau)
- conserve les liens vers les fiches Word locales dans `liens`
- ne modifie pas le fichier JSON original

---

## 📂 Importer des fiches Word

### Méthode recommandée (modèles Word)

1. Ouvre un des 4 modèles Word dans `fiches/`
2. **Sauvegarde-le immédiatement sous un nouveau nom** (ex: `Ortie.docx`) pour garder le modèle vierge
3. Remplis les champs après les `:` — le champ `Type:` en rouge ne doit pas être modifié
4. Sauvegarde en `.docx` dans `Herbier_app/fiches/`
5. Dans l'app → clique sur **"📂 Importer"**

### Format minimal accepté

```
Nom commun: Ortie
Type: plante brute
```

Les labels sont insensibles à la casse. Les champs inconnus sont ignorés.
Les champs multilignes se terminent quand un nouveau label est reconnu.

### Types reconnus dans le champ Type:

| Valeur dans la fiche | Type créé |
|---|---|
| `plante brute`, `brute`, `tisane` | 🌿 Plante brute |
| `complément`, `complement` | 💊 Complément |
| `huile essentielle`, `he`, `huile` | 💧 Huile essentielle |
| `plante jardin`, `jardin` | 🌱 Plante de jardin |

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

Chaque classe hérite des attributs communs de `Plante` et ajoute ses propres champs spécifiques.

### Base de données (`database.py`)

Architecture en tables séparées (une par type) :

| Table | Contenu |
|---|---|
| `plantes` | Champs communs à tous les types |
| `plantes_brutes` | Champs spécifiques PlanteBrute |
| `complements` | Champs spécifiques Complement |
| `huiles_essentielles` | Champs spécifiques HuileEssentielle |
| `plantes_jardin` | Champs spécifiques PlanteJardin |
| `journal` | Journal de cure (lié par `plante_id`) |

> ⚠️ `CHAMPS_SPECIFIQUES` est défini dans `database.py`, pas dans `models.py`
> ```python
> # ❌  from models import CHAMPS_SPECIFIQUES
> # ✅  from database import CHAMPS_SPECIFIQUES
> ```

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

**Fermeture onglet :** `window.close()` peut être bloqué par certains navigateurs. Flask s'arrête bien dans tous les cas — fermer l'onglet manuellement si besoin.

**Double ouverture navigateur :** le mode `debug=True` redémarre Flask à chaque modification de code, ce qui rouvre le navigateur. Comportement normal du reloader.

**Serveur de dev :** le `WARNING: This is a development server` est normal pour un usage local. Ne pas exposer sur internet sans serveur WSGI (Gunicorn, Waitress...).

---

## ➕ Ajouter un nouveau type de plante

**Étape 1** — `models.py` : créer la classe + ajouter dans `TYPE_LABELS`, `TYPE_COULEURS`, `CLASSES_MAP`

**Étape 2** — `database.py` : créer la table + ajouter dans `TABLE_SPECIFIQUE` et `CHAMPS_SPECIFIQUES`

**Étape 3** — `templates/formulaire.html` : ajouter le bloc de champs

**Étape 4** — `templates/detail.html` : ajouter la vue détail

**Étape 5** — `templates/base.html` : ajouter l'option dans le dropdown "+ Ajouter"

---

## 🔁 Workflow Git

```bash
# Modifications courantes
git add .
git commit -m "description de ce qui a changé"
git push

# Premier push (une seule fois)
git init
git remote add origin https://github.com/HAMIDISOF/mon-herbier.git
git push -u origin main --force
```

> `git remote add` → une seule fois. Si `error: remote origin already exists` → sauter cette ligne.

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

## 📅 Évolutions prévues

- [ ] Alertes stock faible
- [ ] Export PDF des fiches
- [ ] Impression de fiches
- [ ] Gestion de la bibliothèque (livres de référence)
- [ ] Statistiques de consommation
- [ ] Déduplication à l'import (éviter les doublons)
- [ ] Mode hors-ligne (PWA) pour usage mobile sans WiFi

---

## 📋 Historique des versions

| Version | Description |
|---|---|
| v1.0 | Première version Tkinter — interface graphique Python desktop |
| v2.0 | Tkinter — ajout des classes PlanteBrute / Complement / HuileEssentielle |
| v3.0 | Migration Flask + SQLite — architecture modulaire (models / database / extract / app) |
| v3.1 | Correction imports CHAMPS_SPECIFIQUES — ouverture auto navigateur — bouton Quitter |
| v4.0 | Responsive mobile — accès WiFi — 4 modèles Word — README complet |

---

*Dernière mise à jour : février 2026 — v4.0*
