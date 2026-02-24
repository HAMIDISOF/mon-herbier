# 🌿 Mon Herbier — v3.0

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
├── herbier.db          ← Base SQLite (créée au 1er lancement)
├── fiches/             ← Dossier de dépôt des fiches .docx à importer
│   └── MODELE_FICHE.txt ← Modèles de fiches pour chaque type
└── templates/
    ├── base.html       ← Navigation, thème, flashs
    ├── index.html      ← Liste + recherche + filtres
    ├── detail.html     ← Fiche détail + journal de cure
    ├── formulaire.html ← Ajout / modification
    └── journal.html    ← Journal global
```

---

## 🚀 Installation & lancement

```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Lancer l'application
python app.py

# 3. Ouvrir dans le navigateur
# → http://localhost:5000
```

---

## 🔄 Migration depuis l'ancienne version

Si tu as un fichier `herbier_data.json` (ancienne version Tkinter) :

```bash
# Place herbier_data.json dans le dossier Herbier_app/
python migrate.py
```

Le script détecte automatiquement les types, migre tous les champs et conserve les liens vers les fiches Word.

---

## 📂 Importer des fiches Word

1. Crée tes fiches `.docx` en suivant le format du fichier `fiches/MODELE_FICHE.txt`
2. Dépose-les dans le dossier `fiches/`
3. Clique sur **"📂 Importer fiches"** dans la barre de navigation

Structure minimale d'une fiche :
```
Nom commun: Ortie
Type: plante brute
```

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

Architecture en tables séparées :
- `plantes` — champs communs à tous les types
- `plantes_brutes` / `complements` / `huiles_essentielles` / `plantes_jardin` — champs spécifiques
- `journal` — entrées du journal de cure (liées par `plante_id`)

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
| POST | `/importer` | Import fiches .docx |
| GET | `/api/plantes` | API JSON |

---

## ➕ Ajouter un nouveau type de plante

**Étape 1** — `models.py` : créer la classe
```python
@dataclass
class PlanteNouveau(Plante):
    TYPE: str = field(default="nouveau", init=False)
    mon_champ: str = ""
```

**Étape 2** — `models.py` : ajouter dans les constantes
```python
TYPE_LABELS   = { ..., "nouveau": "🌺 Nouveau type" }
TYPE_COULEURS = { ..., "nouveau": "#aa6688" }
CLASSES_MAP   = { ..., "nouveau": PlanteNouveau }
```

**Étape 3** — `database.py` : créer la table et ajouter dans les mappings
```python
# Dans init_db() :
c.execute("CREATE TABLE IF NOT EXISTS plantes_nouveau (...)")
# Dans TABLE_SPECIFIQUE et CHAMPS_SPECIFIQUES : ajouter "nouveau"
```

**Étape 4** — `templates/formulaire.html` : ajouter le bloc de champs

**Étape 5** — `templates/detail.html` : ajouter la vue détail

---

## 📅 Évolutions prévues

- [ ] Alertes stock faible
- [ ] Export PDF des fiches
- [ ] Impression de fiches
- [ ] Gestion de la bibliothèque (livres de référence)
- [ ] Statistiques de consommation

---

## 🎨 Thème visuel

Tons naturels, typographie Cormorant Garamond + DM Sans.

| Variable CSS | Couleur | Usage |
|---|---|---|
| `--bg` | Beige clair | Fond général |
| `--paper` | Blanc cassé | Cards, formulaires |
| `--vert` / `--vert2` | Vert foncé | Plantes brutes, actions principales |
| `--brun` | Brun | Précautions |
| `--rouge` | Rouge brique | Contre-indications, suppression |
| `--bleu` | Bleu-gris | Compléments |

---

*Dernière mise à jour : février 2026 — v3.0 Flask*
