# 🌿 Mon Herbier — Schéma des classes

## Diagramme d'héritage

```
┌─────────────────────────────────────────────────────┐
│                      Plante                          │
│                   (classe de base)                   │
├─────────────────────────────────────────────────────┤
│ Attributs communs à tous les types :                 │
│                                                      │
│  id             str   identifiant unique généré auto │
│  nom            str   nom commun *obligatoire*       │
│  latin          str   nom scientifique               │
│  famille        str   famille botanique              │
│  bio            bool  issu de l'agriculture bio ?    │
│  proprietes     str   indications / bénéfices        │
│  contre         str   contre-indications             │
│  precautions    str   précautions générales          │
│  distributeur   str   fournisseur habituel           │
│  prix           str   prix habituel                  │
│  quantite       str   stock disponible               │
│  stockage       str   lieu de stockage               │
│  notes          str   notes personnelles             │
├─────────────────────────────────────────────────────┤
│ Méthodes :                                           │
│  to_dict()      → dict   sérialisation JSON          │
│  from_dict(d)   → Plante désérialisation JSON        │
└──────────────┬──────────────────────────────────────┘
               │
               │  hérite de (extends)
    ┌──────────┼──────────────────┐
    │          │                  │
    ▼          ▼                  ▼

┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────┐
│   PlanteBrute    │  │   Complement     │  │  HuileEssentielle    │
│  TYPE = "brute"  │  │TYPE="complement" │  │    TYPE = "he"       │
├──────────────────┤  ├──────────────────┤  ├──────────────────────┤
│                  │  │                  │  │                      │
│ partie      str  │  │ partie      str  │  │ organe          str  │
│ origine     str  │  │ origine     str  │  │ origine         str  │
│ mode_prep   str  │  │ reference   str  │  │ mode_obtention  str  │
│ temperature str  │  │ forme       str  │  │ chemotype       str  │
│ temps_inf   str  │  │ dosage      str  │  │ composition     str  │
│ posologie   str  │  │ posologie   str  │  │ voies           str  │
│ condition.  str  │  │ moment_prise str │  │ precautions_    str  │
│                  │  │ duree_cure  str  │  │   voies              │
│                  │  │ condition.  str  │  │ dlc             str  │
└──────────────────┘  └──────────────────┘  └──────────────────────┘

    🌿 Vert            💊 Bleu-gris           💧 Brun-orangé
  Tisane, infusion,   Gélules, comprimés,   Huile pure distillée
  décoction, macérat  ampoules, poudre      ou extraite à froid
```

---

## Détail des attributs par classe

### Plante (base)

| Attribut     | Type  | Description                         | Exemple                    |
|--------------|-------|-------------------------------------|----------------------------|
| id           | str   | Identifiant unique (généré auto)    | `brute_20240215143022`     |
| nom          | str   | Nom commun **obligatoire**          | `Ortie`                    |
| latin        | str   | Nom scientifique                    | `Urtica dioica`            |
| famille      | str   | Famille botanique                   | `Urticacées`               |
| bio          | bool  | Biologique ?                        | `True`                     |
| proprietes   | str   | Indications, bénéfices              | `Diurétique, reminéralisant` |
| contre       | str   | Contre-indications                  | `Grossesse`                |
| precautions  | str   | Précautions d'usage générales       | `Consulter un médecin si...` |
| distributeur | str   | Fournisseur habituel                | `Sana Gaïa`                |
| prix         | str   | Prix habituel                       | `8,50 €`                   |
| quantite     | str   | Quantité en stock                   | `20 sachets`               |
| stockage     | str   | Lieu de rangement                   | `Étagère cuisine`          |
| notes        | str   | Notes et observations perso         | `Très efficace en cure...` |

---

### PlanteBrute (hérite de Plante)

| Attribut         | Type | Description                      | Exemple                  |
|------------------|------|----------------------------------|--------------------------|
| partie           | str  | Partie de la plante utilisée     | `Feuille`                |
| origine          | str  | Provenance géographique          | `France`                 |
| mode_preparation | str  | Mode de préparation              | `Infusion`               |
| temperature      | str  | Température de préparation       | `95°C`                   |
| temps_infusion   | str  | Durée d'infusion/décoction       | `5 à 10 min`             |
| posologie        | str  | Dose recommandée                 | `2 tasses/jour`          |
| conditionnement  | str  | Format du produit                | `Vrac 100g`, `Sachets`   |

---

### Complement (hérite de Plante)

| Attribut        | Type | Description                       | Exemple                  |
|-----------------|------|-----------------------------------|--------------------------|
| partie          | str  | Partie de la plante utilisée      | `Racine`                 |
| origine         | str  | Provenance géographique           | `Chine`                  |
| reference       | str  | Référence produit                 | `Réf. 15270`             |
| forme           | str  | Forme galénique                   | `Gélules`                |
| dosage          | str  | Dosage par unité                  | `405 mg`                 |
| posologie       | str  | Nombre d'unités par jour          | `2 gélules/jour`         |
| moment_prise    | str  | Quand prendre le produit          | `Au milieu des repas`    |
| duree_cure      | str  | Durée de la cure conseillée       | `50 à 100 jours`         |
| conditionnement | str  | Format de vente                   | `Boîte 200 gélules`      |

---

### HuileEssentielle (hérite de Plante)

| Attribut          | Type | Description                     | Exemple                              |
|-------------------|------|---------------------------------|--------------------------------------|
| organe            | str  | Partie distillée                | `Feuilles`                           |
| origine           | str  | Pays / région de production     | `Madagascar`                         |
| mode_obtention    | str  | Procédé d'extraction            | `Distillation à la vapeur d'eau`     |
| chemotype         | str  | Chémotype (CT)                  | `1,8-cinéole, α-terpinéol`           |
| composition       | str  | Composants principaux et %      | `Eucalyptol 50-72%, Sabinène 7-18%`  |
| voies             | str  | Voies d'utilisation             | `Cutanée : principale, Orale : secondaire` |
| precautions_voies | str  | Précautions détaillées par voie | `Voie cutanée : diluer dans HV...`   |
| dlc               | str  | Date limite de consommation     | `28/05/2028`                         |

---

## Flux de données

```
Saisie formulaire
      │
      ▼
  lire(widget)          ← lit n'importe quel type de widget Tkinter
      │
      ▼
  objet Plante          ← attributs mis à jour
      │
      ▼
  to_dict()             ← converti en dictionnaire Python
      │
      ▼
  json.dump()           ← écrit dans herbier_data.json
      │
      ▼
  herbier_data.json     ← fichier de persistance


Chargement au démarrage :

  herbier_data.json
      │
      ▼
  json.load()           ← liste de dictionnaires
      │
      ▼
  Plante.from_dict()    ← crée le bon type d'objet selon _type
      │
      ▼
  liste plantes[]       ← en mémoire pendant toute la session
      │
      ▼
  rafraichir()          ← affiche dans le tableau Treeview
```

---

## Évolutions prévues

```
┌──────────────────────────────────────────────────────┐
│                      Plante                          │
└──────────┬───────────────────────────────────────────┘
           │
    ┌──────┼──────────────────────┐
    │      │                      │
    ▼      ▼                      ▼
PlanteBrute  Complement   HuileEssentielle
    │
    │  (mars 2026)
    ▼
PlanteJardin               ← à créer
  emplacement
  exposition
  type_sol
  periode_semis
  periode_recolte
  vivace
  hivernage
  entretien
```

---

*Dernière mise à jour : février 2026*
