# 🌿 Mon Herbier — Documentation

Application de gestion de plantes médicinales, compléments alimentaires et huiles essentielles.
Développée en Python avec Tkinter, données stockées en JSON.

---

## 📁 Structure des fichiers

```
Herbier/
├── herbier.py          ← programme principal (à lancer)
├── herbier_data.json   ← base de données (créée automatiquement au 1er enregistrement)
├── README.md           ← cette documentation
└── CLASSES.md          ← schéma détaillé des classes
```

---

## 🚀 Lancement

```cmd
python herbier.py
```

Ou depuis VS Code : ouvrir `herbier.py` et cliquer sur ▶

---

## 🏗️ Architecture générale

Le programme est organisé en 4 grandes parties :

### 1. Modèle objet (lignes 16–101)
Les classes Python qui représentent les données.
Voir `CLASSES.md` pour le schéma complet.

### 2. Persistance JSON (lignes 103–119)
Lecture et écriture des données dans `herbier_data.json`.
Chaque objet est converti en dictionnaire pour le stockage.

### 3. Interface graphique — fenêtre principale (lignes 121–280)
- Barre du haut avec titre et bouton "+ Nouvelle plante"
- Barre de recherche avec filtre par type
- Tableau principal (Treeview) avec toutes les plantes
- Barre d'actions en bas (Modifier, Voir, Supprimer, Export/Import)

### 4. Formulaires et vues détail (lignes 282–679)
- `faire_fenetre()` : helper qui crée une fenêtre modale scrollable
- `section()` : crée un séparateur de section dans un formulaire
- `champ()` : crée un champ de saisie (entry, combo, text, fichier, checkbox)
- `lire()` : lit la valeur d'un widget quel que soit son type
- `ouvrir_formulaire()` : formulaire d'ajout/modification adapté au type
- `ouvrir_detail()` : vue lecture seule d'une plante

---

## 🎨 Thème visuel

Les couleurs sont définies comme constantes en haut du fichier :

| Constante | Couleur    | Usage                        |
|-----------|------------|------------------------------|
| `BG`      | Beige clair | Fond général                |
| `PAPER`   | Blanc cassé | Fond des champs de saisie   |
| `VERT`    | Vert foncé  | En-têtes, boutons principaux|
| `VERT2`   | Vert très foncé | Labels de formulaire    |
| `BRUN`    | Brun        | Boutons secondaires, précautions |
| `ROUGE`   | Rouge brique | Contre-indications, suppression |
| `MUTED`   | Gris-brun   | Textes secondaires, notes   |
| `BORDER`  | Beige moyen | Bordures, séparateurs       |
| `FG`      | Brun très foncé | Texte principal         |

Chaque type de plante a aussi sa propre couleur d'accent :

| Type        | Couleur  |
|-------------|----------|
| Plante brute | Vert    |
| Complément  | Bleu-gris |
| HE          | Brun-orangé |

---

## ➕ Ajouter un nouveau type de plante

Pour ajouter un nouveau type (ex: `PlanteJardin`) :

**Étape 1** — Créer la classe dans la section MODÈLE OBJET :
```python
class PlanteJardin(Plante):
    TYPE = "jardin"
    def __init__(self):
        super().__init__()
        self.emplacement = ""
        self.exposition  = ""
        # ... autres attributs
```

**Étape 2** — Ajouter le cas dans `Plante.from_dict()` :
```python
elif t == "jardin":
    p = PlanteJardin()
```

**Étape 3** — Ajouter le label et la couleur :
```python
TYPE_LABELS   = { ..., "jardin": "🌱 Jardin" }
TYPE_COULEURS = { ..., "jardin": "#6a8a4a" }
```

**Étape 4** — Ajouter l'option dans le menu "+ Nouvelle plante" :
```python
m.add_command(label="🌱  Plante de jardin",
              command=lambda: ouvrir_formulaire(type_="jardin"))
```

**Étape 5** — Ajouter le filtre dans `type_filtre()` :
```python
if "Jardin" in type_str: return "jardin"
```

**Étape 6** — Ajouter le bloc de champs dans `ouvrir_formulaire()` :
```python
elif type_ == "jardin":
    section(frame, "— Culture")
    cs["emplacement"] = champ(frame, "Emplacement", val("emplacement"))
    cs["exposition"]  = champ(frame, "Exposition",  val("exposition"), "combo",
        ["Plein soleil", "Mi-ombre", "Ombre"])
```

**Étape 7** — Ajouter les infos dans `ouvrir_detail()` :
```python
elif p.TYPE == "jardin":
    infos = [("Emplacement", p.emplacement), ("Exposition", p.exposition)]
```

**Étape 8** — Ajouter l'option dans le filtre combobox de la barre de recherche :
```python
values=["Tous", "🌿 Plante brute", "💊 Complément", "💧 Huile essentielle", "🌱 Jardin"]
```

---

## ➕ Ajouter un champ à un type existant

Ex: ajouter `altitude` à `HuileEssentielle` :

**Étape 1** — Dans la classe `HuileEssentielle.__init__()` :
```python
self.altitude = ""
```

**Étape 2** — Dans `ouvrir_formulaire()`, bloc `type_ == "he"` :
```python
cs["altitude"] = champ(frame, "Altitude de culture", val("altitude"))
```

**Étape 3** — Dans `ouvrir_detail()`, liste `infos` du bloc `he` :
```python
infos = [..., ("Altitude", p.altitude)]
```

Les données existantes en JSON sont compatibles : les anciens enregistrements
n'auront simplement pas ce champ, ce qui est géré proprement par `from_dict()`.

---

## 💾 Format des données JSON

Chaque plante est un objet JSON avec un champ `_type` qui indique la classe :

```json
{
  "_type": "he",
  "id": "he_20240215143022123456",
  "nom": "Ravintsara",
  "latin": "Cinnamomum camphora",
  "famille": "",
  "bio": true,
  "proprietes": "Antiviral, immunostimulant...",
  "contre": "Femmes enceintes...",
  "precautions": "Test cutané préalable...",
  "organe": "Feuilles",
  "origine": "Madagascar",
  "mode_obtention": "Distillation à la vapeur d'eau",
  "chemotype": "1,8-cinéole, α-terpinéol",
  "composition": "Eucalyptol 50-72%, α-terpinéol 4-11%...",
  "voies": "Cutanée : principale\nDiffusion : principale\nOrale : secondaire",
  "dlc": "28/05/2028",
  "distributeur": "Onatera",
  "prix": "12,50 €",
  "quantite": "10ml",
  "stockage": "Placard salle de bain",
  "notes": ""
}
```

---

## 🔄 Export / Import

- **Exporter** : crée un fichier `.json` horodaté avec toutes les plantes
- **Importer** : remplace toutes les données actuelles par celles du fichier importé
- ⚠️ Toujours exporter avant d'importer pour ne pas perdre de données !

---

## 📅 Évolutions prévues

- [ ] Classe `PlanteJardin` (mars) : emplacement, exposition, période de récolte...
- [ ] Import automatique depuis fiches Word/PDF structurées
- [ ] Gestion de la bibliothèque (livres de référence)
- [ ] Alertes stock faible
- [ ] Impression de fiches

---

*Dernière mise à jour : février 2026*
