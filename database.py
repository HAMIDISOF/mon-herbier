# -*- coding: utf-8 -*-
"""
database.py — Couche SQLite de Mon Herbier
===========================================
Responsabilités :
  - Création des tables au premier lancement
  - CRUD complet pour Plante et EntreeJournal
  - Requêtes de recherche et de filtrage

Une seule connexion par appel (sqlite3 thread-safe en mode WAL).
"""

import sqlite3
import os
from models import (
    Plante, PlanteBrute, Complement, HuileEssentielle, PlanteJardin,
    EntreeJournal, creer_plante
)

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "herbier.db")


# ══════════════════════════════════════════════════════════════════════════════
# CONNEXION
# ══════════════════════════════════════════════════════════════════════════════

def get_conn():
    """Retourne une connexion SQLite avec Row factory (accès par nom de colonne)."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")   # meilleure concurrence
    conn.execute("PRAGMA foreign_keys=ON")    # intégrité référentielle
    return conn


# ══════════════════════════════════════════════════════════════════════════════
# INITIALISATION DES TABLES
# ══════════════════════════════════════════════════════════════════════════════

def init_db():
    """
    Crée toutes les tables si elles n'existent pas encore.
    Appelée au démarrage de l'application Flask.
    """
    conn = get_conn()
    c = conn.cursor()

    # Table principale — champs communs à tous les types
    c.execute("""
    CREATE TABLE IF NOT EXISTS plantes (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        type         TEXT    NOT NULL,   -- brute | complement | he | jardin
        nom          TEXT    NOT NULL,
        latin        TEXT    DEFAULT '',
        famille      TEXT    DEFAULT '',
        bio          INTEGER DEFAULT 0,  -- 0=non, 1=oui
        proprietes   TEXT    DEFAULT '',
        contre       TEXT    DEFAULT '',
        interactions TEXT    DEFAULT '',
        precautions  TEXT    DEFAULT '',
        distributeur TEXT    DEFAULT '',
        prix         TEXT    DEFAULT '',
        quantite     TEXT    DEFAULT '',
        stockage     TEXT    DEFAULT '',
        liens        TEXT    DEFAULT '',
        notes        TEXT    DEFAULT ''
    )""")

    # Attributs spécifiques PlanteBrute
    c.execute("""
    CREATE TABLE IF NOT EXISTS plantes_brutes (
        plante_id         INTEGER PRIMARY KEY REFERENCES plantes(id) ON DELETE CASCADE,
        partie            TEXT DEFAULT '',
        origine           TEXT DEFAULT '',
        mode_preparation  TEXT DEFAULT '',
        temperature       TEXT DEFAULT '',
        temps_infusion    TEXT DEFAULT '',
        posologie         TEXT DEFAULT '',
        conditionnement   TEXT DEFAULT ''
    )""")

    # Attributs spécifiques Complement
    c.execute("""
    CREATE TABLE IF NOT EXISTS complements (
        plante_id        INTEGER PRIMARY KEY REFERENCES plantes(id) ON DELETE CASCADE,
        partie           TEXT DEFAULT '',
        origine          TEXT DEFAULT '',
        reference        TEXT DEFAULT '',
        forme            TEXT DEFAULT '',
        dosage           TEXT DEFAULT '',
        posologie        TEXT DEFAULT '',
        moment_prise     TEXT DEFAULT '',
        duree_cure       TEXT DEFAULT '',
        conditionnement  TEXT DEFAULT ''
    )""")

    # Attributs spécifiques HuileEssentielle
    c.execute("""
    CREATE TABLE IF NOT EXISTS huiles_essentielles (
        plante_id          INTEGER PRIMARY KEY REFERENCES plantes(id) ON DELETE CASCADE,
        organe             TEXT DEFAULT '',
        origine            TEXT DEFAULT '',
        mode_obtention     TEXT DEFAULT '',
        chemotype          TEXT DEFAULT '',
        composition        TEXT DEFAULT '',
        voies              TEXT DEFAULT '',
        precautions_voies  TEXT DEFAULT '',
        dlc                TEXT DEFAULT ''
    )""")

    # Attributs spécifiques PlanteJardin
    c.execute("""
    CREATE TABLE IF NOT EXISTS plantes_jardin (
        plante_id        INTEGER PRIMARY KEY REFERENCES plantes(id) ON DELETE CASCADE,
        partie           TEXT    DEFAULT '',
        emplacement      TEXT    DEFAULT '',
        exposition       TEXT    DEFAULT '',
        type_sol         TEXT    DEFAULT '',
        periode_semis    TEXT    DEFAULT '',
        periode_recolte  TEXT    DEFAULT '',
        vivace           INTEGER DEFAULT 0,
        hivernage        TEXT    DEFAULT '',
        entretien        TEXT    DEFAULT ''
    )""")

    # Journal de cures
    c.execute("""
    CREATE TABLE IF NOT EXISTS journal (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        plante_id  INTEGER NOT NULL REFERENCES plantes(id) ON DELETE CASCADE,
        date       TEXT    NOT NULL,
        action     TEXT    DEFAULT '',
        notes      TEXT    DEFAULT ''
    )""")

    conn.commit()
    conn.close()
    print("✅ Base de données initialisée.")


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS INTERNES
# ══════════════════════════════════════════════════════════════════════════════

TABLE_SPECIFIQUE = {
    "brute":      "plantes_brutes",
    "complement": "complements",
    "he":         "huiles_essentielles",
    "jardin":     "plantes_jardin",
}

CHAMPS_SPECIFIQUES = {
    "brute":      ["partie", "origine", "mode_preparation", "temperature",
                   "temps_infusion", "posologie", "conditionnement"],
    "complement": ["partie", "origine", "reference", "forme", "dosage",
                   "posologie", "moment_prise", "duree_cure", "conditionnement"],
    "he":         ["organe", "origine", "mode_obtention", "chemotype",
                   "composition", "voies", "precautions_voies", "dlc"],
    "jardin":     ["partie", "emplacement", "exposition", "type_sol",
                   "periode_semis", "periode_recolte", "vivace", "hivernage", "entretien"],
}

CHAMPS_COMMUNS = ["nom", "latin", "famille", "bio", "proprietes", "contre",
                  "interactions", "precautions", "distributeur", "prix",
                  "quantite", "stockage", "liens", "notes"]

def _row_to_plante(row_base, row_spec, type_: str) -> Plante:
    """Reconstruit un objet Plante à partir de deux lignes SQLite."""
    obj = creer_plante(type_)
    obj.id = row_base["id"]
    for champ in CHAMPS_COMMUNS:
        setattr(obj, champ, row_base[champ])
    obj.bio = bool(row_base["bio"])
    if row_spec:
        for champ in CHAMPS_SPECIFIQUES.get(type_, []):
            val = row_spec[champ]
            if champ == "vivace":
                val = bool(val)
            setattr(obj, champ, val)
    return obj


# ══════════════════════════════════════════════════════════════════════════════
# CRUD PLANTES
# ══════════════════════════════════════════════════════════════════════════════

def lister_plantes(type_filtre: str = None, recherche: str = None) -> list[Plante]:
    """
    Retourne toutes les plantes, avec filtres optionnels.
    type_filtre : "brute" | "complement" | "he" | "jardin" | None
    recherche   : texte libre cherché dans nom, latin, proprietes
    """
    conn = get_conn()
    c = conn.cursor()

    sql = "SELECT * FROM plantes WHERE 1=1"
    params = []

    if type_filtre:
        sql += " AND type = ?"
        params.append(type_filtre)

    if recherche:
        sql += " AND (nom LIKE ? OR latin LIKE ? OR proprietes LIKE ?)"
        terme = f"%{recherche}%"
        params.extend([terme, terme, terme])

    sql += " ORDER BY nom COLLATE NOCASE"
    rows = c.execute(sql, params).fetchall()

    plantes = []
    for row in rows:
        t = row["type"]
        table = TABLE_SPECIFIQUE.get(t)
        row_spec = None
        if table:
            row_spec = c.execute(
                f"SELECT * FROM {table} WHERE plante_id = ?", (row["id"],)
            ).fetchone()
        plantes.append(_row_to_plante(row, row_spec, t))

    conn.close()
    return plantes


def get_plante(plante_id: int) -> Plante | None:
    """Retourne une plante par son id, ou None si introuvable."""
    conn = get_conn()
    c = conn.cursor()
    row = c.execute("SELECT * FROM plantes WHERE id = ?", (plante_id,)).fetchone()
    if not row:
        conn.close()
        return None
    t = row["type"]
    table = TABLE_SPECIFIQUE.get(t)
    row_spec = c.execute(
        f"SELECT * FROM {table} WHERE plante_id = ?", (plante_id,)
    ).fetchone() if table else None
    obj = _row_to_plante(row, row_spec, t)
    conn.close()
    return obj


def sauvegarder_plante(obj: Plante) -> int:
    """
    Insère ou met à jour une plante (INSERT si id=None, UPDATE sinon).
    Retourne l'id de la plante.
    """
    conn = get_conn()
    c = conn.cursor()
    communs = {ch: getattr(obj, ch) for ch in CHAMPS_COMMUNS}
    communs["bio"] = int(obj.bio)

    if obj.id is None:
        # INSERT
        cols = ", ".join(["type"] + list(communs.keys()))
        placeholders = ", ".join(["?"] * (1 + len(communs)))
        vals = [obj.TYPE] + list(communs.values())
        c.execute(f"INSERT INTO plantes ({cols}) VALUES ({placeholders})", vals)
        plante_id = c.lastrowid
    else:
        # UPDATE
        plante_id = obj.id
        set_clause = ", ".join(f"{k}=?" for k in communs)
        vals = list(communs.values()) + [plante_id]
        c.execute(f"UPDATE plantes SET {set_clause} WHERE id=?", vals)

    # Champs spécifiques
    table = TABLE_SPECIFIQUE.get(obj.TYPE)
    if table:
        champs = CHAMPS_SPECIFIQUES[obj.TYPE]
        spec = {}
        for ch in champs:
            val = getattr(obj, ch, "")
            if ch == "vivace":
                val = int(val)
            spec[ch] = val

        existing = c.execute(
            f"SELECT plante_id FROM {table} WHERE plante_id=?", (plante_id,)
        ).fetchone()

        if existing:
            set_clause = ", ".join(f"{k}=?" for k in spec)
            c.execute(
                f"UPDATE {table} SET {set_clause} WHERE plante_id=?",
                list(spec.values()) + [plante_id]
            )
        else:
            cols = "plante_id, " + ", ".join(spec.keys())
            placeholders = ", ".join(["?"] * (1 + len(spec)))
            c.execute(
                f"INSERT INTO {table} ({cols}) VALUES ({placeholders})",
                [plante_id] + list(spec.values())
            )

    conn.commit()
    conn.close()
    return plante_id


def supprimer_plante(plante_id: int):
    """Supprime une plante et toutes ses données liées (CASCADE)."""
    conn = get_conn()
    conn.execute("DELETE FROM plantes WHERE id=?", (plante_id,))
    conn.commit()
    conn.close()


# ══════════════════════════════════════════════════════════════════════════════
# CRUD JOURNAL
# ══════════════════════════════════════════════════════════════════════════════

def get_journal(plante_id: int) -> list[EntreeJournal]:
    """Retourne toutes les entrées du journal pour une plante, triées par date desc."""
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM journal WHERE plante_id=? ORDER BY date DESC", (plante_id,)
    ).fetchall()
    conn.close()
    return [EntreeJournal(
        id=r["id"], plante_id=r["plante_id"],
        date=r["date"], action=r["action"], notes=r["notes"]
    ) for r in rows]


def get_journal_global() -> list[dict]:
    """Retourne toutes les entrées du journal toutes plantes confondues."""
    conn = get_conn()
    rows = conn.execute("""
        SELECT j.*, p.nom, p.type FROM journal j
        JOIN plantes p ON j.plante_id = p.id
        ORDER BY j.date DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def ajouter_entree_journal(entree: EntreeJournal) -> int:
    """Ajoute une entrée dans le journal. Retourne l'id créé."""
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "INSERT INTO journal (plante_id, date, action, notes) VALUES (?,?,?,?)",
        (entree.plante_id, entree.date, entree.action, entree.notes)
    )
    conn.commit()
    new_id = c.lastrowid
    conn.close()
    return new_id


def supprimer_entree_journal(entree_id: int):
    """Supprime une entrée du journal."""
    conn = get_conn()
    conn.execute("DELETE FROM journal WHERE id=?", (entree_id,))
    conn.commit()
    conn.close()
