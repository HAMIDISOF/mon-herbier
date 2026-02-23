"""
Mon Herbier - Gestion de plantes médicinales
=========================================
Architecture orientée objet :
  Plante (base) > PlanteBrute / Complement / HuileEssentielle

Fichiers :
  herbier.py          → ce fichier, programme principal
  herbier_data.json   → base de données (créée automatiquement)
  README.md           → documentation générale
  CLASSES.md          → schéma détaillé des classes

Pour lancer : python herbier.py
Pour la doc  : voir README.md
"""

# ── Bibliothèques utilisées ─────────────────────────────────────────────────
import tkinter as tk                          # interface graphique standard Python
from tkinter import ttk, messagebox, filedialog  # widgets avancés, boîtes de dialogue
import json                                   # lecture/écriture des données
import os                                     # chemins de fichiers
from datetime import datetime                 # génération des identifiants uniques

# ══════════════════════════════════════════════════════════════════════════════
# MODÈLE OBJET
# ══════════════════════════════════════════════════════════════════════════════

class Plante:
    """
    Classe de BASE — commune à tous les types de plantes.

    Tous les attributs définis ici sont disponibles dans les sous-classes.
    Ne pas instancier directement : utiliser PlanteBrute, Complement ou HuileEssentielle.

    L'attribut TYPE (chaîne) identifie le type dans le JSON :
      "brute" | "complement" | "he"
    """
    TYPE = "base"  # redéfini dans chaque sous-classe

    def __init__(self):
        self.id            = ""
        self.nom           = ""
        self.latin         = ""
        self.famille       = ""
        self.proprietes    = ""   # bénéfices / indications
        self.contre        = ""   # contre-indications
        self.precautions   = ""
        self.distributeur  = ""
        self.prix          = ""
        self.quantite      = ""
        self.stockage      = ""
        self.bio           = False
        self.notes         = ""

    def to_dict(self):
        """
        Convertit l'objet en dictionnaire pour la sauvegarde JSON.
        Ajoute automatiquement la clé "_type" pour pouvoir recréer
        le bon type d'objet au chargement.
        """
        return {"_type": self.TYPE, **self.__dict__}

    @staticmethod
    def from_dict(d):
        """
        Recrée un objet du bon type à partir d'un dictionnaire JSON.
        Lit la clé "_type" pour choisir la classe, puis copie
        tous les attributs. Les attributs inconnus sont ignorés
        (compatibilité si on ajoute des champs plus tard).
        """
        t = d.get("_type", "brute")  # "brute" par défaut si la clé manque
        if t == "brute":
            p = PlanteBrute()
        elif t == "complement":
            p = Complement()
        elif t == "he":
            p = HuileEssentielle()
        else:
            p = PlanteBrute()
        for k, v in d.items():
            if k != "_type" and hasattr(p, k):
                setattr(p, k, v)
        return p


class PlanteBrute(Plante):
    """
    Plante utilisée sous forme brute : tisane, décoction, macérat, teinture...
    Hérite de tous les attributs de Plante et ajoute les infos
    spécifiques à la préparation et à la botanique.
    """
    TYPE = "brute"

    def __init__(self):
        super().__init__()
        self.partie           = ""
        self.origine          = ""
        self.mode_preparation = ""
        self.temperature      = ""
        self.temps_infusion   = ""
        self.posologie        = ""
        self.conditionnement  = ""


class Complement(Plante):
    """
    Complément alimentaire sous forme de produit fini.
    Exemples : Ginkgo Biloba en gélules, Kudzu en comprimés...
    Hérite de Plante et ajoute les infos produit (référence, dosage, posologie).
    """
    TYPE = "complement"

    def __init__(self):
        super().__init__()
        self.partie           = ""
        self.origine          = ""
        self.reference        = ""
        self.forme            = ""
        self.dosage           = ""
        self.posologie        = ""
        self.moment_prise     = ""
        self.duree_cure       = ""
        self.conditionnement  = ""


class HuileEssentielle(Plante):
    """
    Huile essentielle pure (non mélangée).
    Exemples : Ravintsara, Lavande vraie, Tea Tree...
    Hérite de Plante et ajoute les infos spécifiques aux HE :
    origine, mode d'obtention, chémotype, voies d'utilisation, DLC.
    """
    TYPE = "he"

    def __init__(self):
        super().__init__()
        self.organe             = ""
        self.origine            = ""
        self.mode_obtention     = ""
        self.chemotype          = ""
        self.composition        = ""
        self.voies              = ""
        self.precautions_voies  = ""
        self.dlc                = ""


# ══════════════════════════════════════════════════════════════════════════════
# PERSISTANCE JSON
# ══════════════════════════════════════════════════════════════════════════════

# Chemin absolu vers le fichier JSON, dans le même dossier que herbier.py
# os.path.abspath(__file__) donne le chemin complet de ce script
# os.path.dirname() en extrait le dossier parent
FICHIER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "herbier_data.json")

def charger():
    """
    Charge toutes les plantes depuis le fichier JSON.
    Retourne une liste vide si le fichier n'existe pas encore
    (premier lancement de l'application).
    Chaque dictionnaire est converti en objet du bon type via from_dict().
    """
    if os.path.exists(FICHIER):
        with open(FICHIER, "r", encoding="utf-8") as f:
            return [Plante.from_dict(d) for d in json.load(f)]
    return []  # premier lancement : pas encore de données

def sauvegarder(data):
    """
    Sauvegarde toutes les plantes dans le fichier JSON.
    ensure_ascii=False : préserve les accents (é, è, ç...)
    indent=2 : formate le JSON lisiblement (2 espaces d'indentation)
    Appelée automatiquement après chaque ajout, modification, suppression.
    """
    with open(FICHIER, "w", encoding="utf-8") as f:
        json.dump([p.to_dict() for p in data], f, ensure_ascii=False, indent=2)

plantes = charger()

# ══════════════════════════════════════════════════════════════════════════════
# COULEURS & THÈME
# ══════════════════════════════════════════════════════════════════════════════

BG     = "#f5f0e8"
PAPER  = "#fdf8f0"
VERT   = "#4a7a35"
VERT2  = "#2d5a1e"
BRUN   = "#8b6f3e"
MUTED  = "#7a6d5a"
BORDER = "#c4b99a"
ROUGE  = "#8b3a2a"
FG     = "#2c2416"

# Libellés affichés dans l'interface pour chaque type
# → Pour ajouter un type : ajouter une entrée ici ET dans TYPE_COULEURS
TYPE_LABELS = {
    "brute":      "🌿 Plante brute",
    "complement": "💊 Complément",
    "he":         "💧 Huile essentielle",
}
# Couleur d'accent de chaque type (en-tête fiche détail, labels)
TYPE_COULEURS = {
    "brute":      "#4a7a35",  # vert
    "complement": "#5a6a8a",  # bleu-gris
    "he":         "#8a5a2a",  # brun-orangé
}

# ══════════════════════════════════════════════════════════════════════════════
# FENÊTRE PRINCIPALE
# ══════════════════════════════════════════════════════════════════════════════

root = tk.Tk()
root.title("🌿 Mon Herbier")
root.geometry("1200x720")
root.configure(bg=BG)
root.minsize(900, 500)

style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview",
    background=PAPER, fieldbackground=PAPER, foreground=FG,
    rowheight=28, font=("Georgia", 11), borderwidth=0)
style.configure("Treeview.Heading",
    background=VERT, foreground="white", font=("Georgia", 11, "bold"), relief="flat")
style.map("Treeview",
    background=[("selected", VERT)], foreground=[("selected", "white")])

# ── Barre du haut ─────────────────────────────────────────────────────────────
top_bar = tk.Frame(root, bg=VERT, pady=12)
top_bar.pack(fill="x")

tk.Label(top_bar, text="🌿 Mon Herbier", bg=VERT, fg="white",
         font=("Georgia", 18, "bold")).pack(side="left", padx=20)
tk.Label(top_bar, text="Carnet de plantes médicinales", bg=VERT, fg="#c8dfc0",
         font=("Georgia", 10, "italic")).pack(side="left")

def menu_nouvelle(event=None):
    m = tk.Menu(root, tearoff=0, bg=PAPER, fg=FG, font=("Georgia", 10),
                activebackground=VERT, activeforeground="white")
    m.add_command(label="🌿  Plante brute",           command=lambda: ouvrir_formulaire(type_="brute"))
    m.add_command(label="💊  Complément alimentaire",  command=lambda: ouvrir_formulaire(type_="complement"))
    m.add_command(label="💧  Huile essentielle",       command=lambda: ouvrir_formulaire(type_="he"))
    btn_new.update_idletasks()
    m.post(btn_new.winfo_rootx(), btn_new.winfo_rooty() + btn_new.winfo_height())

btn_new = tk.Button(top_bar, text="+ Nouvelle plante ▾", bg=PAPER, fg=VERT2,
                    font=("Georgia", 10, "bold"), relief="flat", padx=12, pady=4,
                    cursor="hand2", command=menu_nouvelle)
btn_new.pack(side="right", padx=8)

# ── Barre de recherche ────────────────────────────────────────────────────────
search_bar = tk.Frame(root, bg=BG, pady=10)
search_bar.pack(fill="x", padx=20)

tk.Label(search_bar, text="🔍", bg=BG, font=("Georgia", 12)).pack(side="left")
search_var = tk.StringVar()
tk.Entry(search_bar, textvariable=search_var, font=("Georgia", 12),
         bg=PAPER, fg=FG, relief="solid", bd=1, width=35).pack(side="left", padx=8, ipady=4)
search_var.trace_add("write", lambda *a: rafraichir())

tk.Label(search_bar, text="Type :", bg=BG, fg=MUTED, font=("Georgia", 10)).pack(side="left", padx=(16, 4))
type_var = tk.StringVar(value="Tous")
ttk.Combobox(search_bar, textvariable=type_var,
             values=["Tous", "🌿 Plante brute", "💊 Complément", "💧 Huile essentielle"],
             state="readonly", width=22, font=("Georgia", 10)).pack(side="left")
type_var.trace_add("write", lambda *a: rafraichir())

stats_label = tk.Label(search_bar, text="", bg=BG, fg=MUTED, font=("Georgia", 9, "italic"))
stats_label.pack(side="right", padx=10)

# ── Tableau principal ─────────────────────────────────────────────────────────
main_frame = tk.Frame(root, bg=BG)
main_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))

colonnes = ("type", "nom", "latin", "proprietes", "contre", "quantite", "distributeur", "prix")
entetes  = ("Type", "Nom", "Nom latin", "Indications", "Contre-indications", "Quantité", "Distributeur", "Prix")
largeurs = (130, 150, 160, 220, 180, 90, 140, 80)

tree = ttk.Treeview(main_frame, columns=colonnes, show="headings", selectmode="browse")
for col, ent, larg in zip(colonnes, entetes, largeurs):
    tree.heading(col, text=ent)
    tree.column(col, width=larg, minwidth=60)

sy = ttk.Scrollbar(main_frame, orient="vertical",  command=tree.yview)
sx = ttk.Scrollbar(main_frame, orient="horizontal", command=tree.xview)
tree.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
tree.grid(row=0, column=0, sticky="nsew")
sy.grid(row=0, column=1, sticky="ns")
sx.grid(row=1, column=0, sticky="ew")
main_frame.rowconfigure(0, weight=1)
main_frame.columnconfigure(0, weight=1)

tree.tag_configure("brute",      background="#eef5e8")
tree.tag_configure("complement", background="#e8ecf5")
tree.tag_configure("he",         background="#f5ede8")

tree.bind("<Double-1>", lambda e: voir_selection())

# ══════════════════════════════════════════════════════════════════════════════
# LOGIQUE PRINCIPALE
# ══════════════════════════════════════════════════════════════════════════════

def type_filtre(type_str):
    if type_str == "Tous": return None
    if "Plante" in type_str:     return "brute"
    if "Complément" in type_str: return "complement"
    if "Huile" in type_str:      return "he"
    return None

def rafraichir():
    """
    Recharge l'affichage du tableau selon les filtres actifs.
    Appelée automatiquement à chaque frappe dans la recherche,
    changement de filtre, et après toute modification des données.
    """
    q  = search_var.get().lower()   # texte recherché (en minuscules pour comparaison)
    tf = type_filtre(type_var.get()) # type filtré (None = tous)
    filtrees = []
    for p in plantes:
        if tf and p.TYPE != tf:
            continue
        champs_txt = " ".join(str(getattr(p, a, "")) for a in vars(p))
        if q and q not in champs_txt.lower():
            continue
        filtrees.append(p)
    tree.delete(*tree.get_children())
    for p in filtrees:
        tree.insert("", "end", iid=p.id, tags=(p.TYPE,), values=(
            TYPE_LABELS.get(p.TYPE, p.TYPE),
            p.nom, p.latin, p.proprietes, p.contre,
            p.quantite, p.distributeur, p.prix
        ))
    stats_label.config(text=f"{len(filtrees)} / {len(plantes)} plante(s)")

def get_selected():
    sel = tree.selection()
    if not sel:
        messagebox.showinfo("Info", "Sélectionnez d'abord une plante dans la liste.")
        return None
    return next((p for p in plantes if p.id == sel[0]), None)

def modifier_selection():
    p = get_selected()
    if p: ouvrir_formulaire(plante=p)

def supprimer_selection():
    p = get_selected()
    if not p: return
    if messagebox.askyesno("Confirmer", f"Supprimer « {p.nom} » ?"):
        plantes.remove(p)
        sauvegarder(plantes)
        rafraichir()

def voir_selection():
    p = get_selected()
    if p: ouvrir_detail(p)

def exporter():
    chemin = filedialog.asksaveasfilename(
        defaultextension=".json", filetypes=[("JSON", "*.json")],
        initialfile=f"herbier_{datetime.now().strftime('%Y%m%d')}.json",
        title="Exporter les données")
    if chemin:
        with open(chemin, "w", encoding="utf-8") as f:
            json.dump([p.to_dict() for p in plantes], f, ensure_ascii=False, indent=2)
        messagebox.showinfo("Export", "Données exportées avec succès !")

def importer():
    global plantes
    chemin = filedialog.askopenfilename(filetypes=[("JSON", "*.json")], title="Importer")
    if not chemin: return
    with open(chemin, "r", encoding="utf-8") as f:
        data = [Plante.from_dict(d) for d in json.load(f)]
    if messagebox.askyesno("Importer", f"Importer {len(data)} plante(s) ?\nCela remplacera les données actuelles."):
        plantes = data
        sauvegarder(plantes)
        rafraichir()

# ── Barre d'actions bas ───────────────────────────────────────────────────────
bot_bar = tk.Frame(root, bg=BG, pady=6)
bot_bar.pack(fill="x", padx=20)

def mkbtn(parent, texte, cmd, bg=VERT, fg="white"):
    return tk.Button(parent, text=texte, command=cmd, bg=bg, fg=fg,
                     font=("Georgia", 10), relief="flat", padx=10, pady=4, cursor="hand2")

mkbtn(bot_bar, "✏  Modifier",     modifier_selection).pack(side="left", padx=4)
mkbtn(bot_bar, "👁  Voir fiche",  voir_selection).pack(side="left", padx=4)
mkbtn(bot_bar, "🗑  Supprimer",   supprimer_selection, ROUGE).pack(side="left", padx=4)
mkbtn(bot_bar, "⬇ Exporter JSON", exporter, BRUN).pack(side="right", padx=4)
mkbtn(bot_bar, "⬆ Importer JSON", importer, BRUN).pack(side="right", padx=4)

# ══════════════════════════════════════════════════════════════════════════════
# HELPERS FORMULAIRE
# ══════════════════════════════════════════════════════════════════════════════

def faire_fenetre(titre, geo="700x740"):
    """
    Crée une fenêtre modale (Toplevel) avec :
    - Un en-tête coloré avec le titre
    - Une zone scrollable (Canvas + Scrollbar) pour le contenu
    Retourne (win, frame) : la fenêtre et le frame scrollable dans lequel
    ajouter les widgets.
    """
    win = tk.Toplevel(root)  # fenêtre enfant de la fenêtre principale
    win.title(titre)
    win.geometry(geo)
    win.configure(bg=BG)
    win.grab_set()

    hf = tk.Frame(win, bg=VERT, height=46)
    hf.pack(fill="x")
    hf.pack_propagate(False)
    tk.Label(hf, text=titre, bg=VERT, fg="white",
             font=("Georgia", 13, "bold")).pack(side="left", padx=16, pady=10)

    canvas = tk.Canvas(win, bg=BG, highlightthickness=0)
    sb = ttk.Scrollbar(win, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=sb.set)
    sb.pack(side="right", fill="y")
    canvas.pack(fill="both", expand=True)
    frame = tk.Frame(canvas, bg=BG, padx=24, pady=12)
    cw = canvas.create_window((0, 0), window=frame, anchor="nw")

    def on_conf(e):
        canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.itemconfig(cw, width=canvas.winfo_width())
    frame.bind("<Configure>", on_conf)
    canvas.bind("<Configure>", on_conf)
    canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(-1 * (e.delta // 120), "units"))

    return win, frame

def section(frame, titre):
    f = tk.Frame(frame, bg=BG)
    f.pack(fill="x", pady=(14, 4))
    tk.Label(f, text=titre, bg=BG, fg=VERT,
             font=("Georgia", 11, "bold italic")).pack(side="left")
    tk.Frame(f, bg=BORDER, height=1).pack(side="left", fill="x", expand=True, padx=8, pady=6)

def champ(frame, label, valeur="", type_="entry", options=None, height=3):
    """
    Crée une ligne de formulaire avec un label et un widget de saisie.

    Paramètres :
      frame   : frame parent où ajouter la ligne
      label   : texte affiché à gauche
      valeur  : valeur initiale du champ
      type_   : type de widget :
                  "entry"   → champ texte simple (1 ligne)
                  "text"    → zone de texte multi-lignes
                  "combo"   → liste déroulante (options requises)
                  "check"   → case à cocher oui/non
                  "fichier" → champ texte + bouton Parcourir
      options : liste de valeurs pour type_="combo"
      height  : nombre de lignes pour type_="text"

    Retourne le widget créé (Entry, Text, StringVar pour combo, BooleanVar pour check).
    Pour type_="fichier", le widget Entry a un attribut _nom_widget à relier
    au champ nom pour le remplissage automatique.
    """
    row = tk.Frame(frame, bg=BG)
    row.pack(fill="x", pady=3)
    tk.Label(row, text=label, bg=BG, fg=VERT2, font=("Georgia", 9, "bold"),
             width=26, anchor="w").pack(side="left")

    if type_ == "entry":
        w = tk.Entry(row, font=("Georgia", 11), bg=PAPER, fg=FG, relief="solid", bd=1)
        w.pack(side="left", fill="x", expand=True, ipady=3)
        if valeur: w.insert(0, str(valeur))

    elif type_ == "combo":
        v = tk.StringVar(value=str(valeur) if valeur else "")
        w = ttk.Combobox(row, textvariable=v, values=options or [],
                         state="readonly", font=("Georgia", 11), width=28)
        w.pack(side="left")
        return v

    elif type_ == "check":
        v = tk.BooleanVar(value=bool(valeur))
        tk.Checkbutton(row, variable=v, bg=BG, activebackground=BG,
                       text="Oui", font=("Georgia", 11)).pack(side="left")
        return v

    elif type_ == "text":
        w = tk.Text(row, font=("Georgia", 11), bg=PAPER, fg=FG,
                    relief="solid", bd=1, height=height, wrap="word")
        w.pack(side="left", fill="x", expand=True)
        if valeur: w.insert("1.0", str(valeur))

    elif type_ == "fichier":
        sub = tk.Frame(row, bg=BG)
        sub.pack(side="left", fill="x", expand=True)
        w = tk.Entry(sub, font=("Georgia", 10), bg=PAPER, fg=FG, relief="solid", bd=1)
        w.pack(side="left", fill="x", expand=True, ipady=3)
        if valeur: w.insert(0, str(valeur))
        w._nom_widget = None

        def parcourir(entry=w):
            chemin = filedialog.askopenfilename(
                title="Choisir la fiche",
                filetypes=[("Documents", "*.pdf *.docx *.doc"), ("Tous", "*.*")])
            if chemin:
                entry.delete(0, "end")
                entry.insert(0, chemin)
                if entry._nom_widget and not entry._nom_widget.get().strip():
                    nom = os.path.splitext(os.path.basename(chemin))[0]
                    entry._nom_widget.delete(0, "end")
                    entry._nom_widget.insert(0, nom)

        tk.Button(sub, text="📂 Parcourir", command=parcourir, bg=BRUN, fg="white",
                  font=("Georgia", 9), relief="flat", padx=8, cursor="hand2").pack(side="left", padx=6)

    return w

def lire(w):
    """
    Lit la valeur d'un widget de formulaire quel que soit son type.
    Gère les 4 cas possibles retournés par champ() :
      tk.Text      → getText depuis position 1.0 jusqu'à la fin
      tk.StringVar → pour les Combobox
      tk.BooleanVar→ pour les Checkbutton
      tk.Entry     → cas standard
    """
    if isinstance(w, tk.Text):        return w.get("1.0", "end").strip()
    elif isinstance(w, tk.StringVar): return w.get().strip()
    elif isinstance(w, tk.BooleanVar):return w.get()
    else:                             return w.get().strip()

# ══════════════════════════════════════════════════════════════════════════════
# FORMULAIRE AJOUT / MODIFICATION
# ══════════════════════════════════════════════════════════════════════════════

def ouvrir_formulaire(plante=None, type_=None):
    """
    Ouvre le formulaire d'ajout ou de modification.

    Paramètres :
      plante : objet Plante existant → mode modification
               None               → mode création
      type_  : "brute" | "complement" | "he"
               ignoré si plante est fourni (on utilise plante.TYPE)

    Le formulaire affiche les champs communs (Plante) puis
    les champs spécifiques au type choisi.
    """
    if plante:
        type_ = plante.TYPE  # en modification, le type ne change pas
    if not type_:
        type_ = "brute"      # type par défaut

    label_type = TYPE_LABELS.get(type_, "Plante")
    titre = f"{'Modifier' if plante else 'Nouvelle'} — {label_type}"
    win, frame = faire_fenetre(titre)

    def val(attr):
        return getattr(plante, attr, "") if plante else ""

    # Champs communs
    section(frame, "— Identification")
    w_nom    = champ(frame, "Nom commun *", val("nom"))
    w_latin  = champ(frame, "Nom latin",    val("latin"))
    w_fam    = champ(frame, "Famille",      val("famille"))
    w_bio    = champ(frame, "Biologique",   val("bio"), "check")

    # Champs spécifiques
    cs = {}  # champs spécifiques

    if type_ == "brute":
        section(frame, "— Botanique & Préparation")
        cs["partie"]           = champ(frame, "Partie utilisée", val("partie"), "combo",
            ["Feuille","Fleur","Racine","Écorce","Graine","Fruit","Tige","Plante entière"])
        cs["origine"]          = champ(frame, "Origine", val("origine"))
        cs["mode_preparation"] = champ(frame, "Mode de préparation", val("mode_preparation"), "combo",
            ["Infusion","Décoction","Macérat huileux","Teinture mère","Poudre","Vrac","Sachets","Autre"])
        cs["temperature"]      = champ(frame, "Température", val("temperature"))
        cs["temps_infusion"]   = champ(frame, "Temps d'infusion", val("temps_infusion"))
        cs["posologie"]        = champ(frame, "Posologie", val("posologie"))
        cs["conditionnement"]  = champ(frame, "Conditionnement", val("conditionnement"))

    elif type_ == "complement":
        section(frame, "— Produit")
        cs["reference"]       = champ(frame, "Référence produit", val("reference"))
        cs["partie"]          = champ(frame, "Partie utilisée",   val("partie"))
        cs["origine"]         = champ(frame, "Origine",           val("origine"))
        cs["forme"]           = champ(frame, "Forme", val("forme"), "combo",
            ["Gélules","Comprimés","Ampoules","Poudre","Liquide","Autre"])
        cs["dosage"]          = champ(frame, "Dosage / unité",    val("dosage"))
        cs["posologie"]       = champ(frame, "Posologie",         val("posologie"))
        cs["moment_prise"]    = champ(frame, "Moment de prise",   val("moment_prise"))
        cs["duree_cure"]      = champ(frame, "Durée de cure",     val("duree_cure"))
        cs["conditionnement"] = champ(frame, "Conditionnement",   val("conditionnement"))

    elif type_ == "he":
        section(frame, "— Huile Essentielle")
        cs["organe"]          = champ(frame, "Organe distillé", val("organe"), "combo",
            ["Feuilles","Fleurs","Écorce","Racine","Fruit","Graine","Bois","Résine","Plante entière"])
        cs["origine"]         = champ(frame, "Origine / Pays",   val("origine"))
        cs["mode_obtention"]  = champ(frame, "Mode d'obtention", val("mode_obtention"), "combo",
            ["Distillation à la vapeur d'eau","Expression à froid","CO2 supercritique","Enfleurage","Autre"])
        cs["chemotype"]       = champ(frame, "Chémotype",        val("chemotype"))
        cs["composition"]     = champ(frame, "Composition",      val("composition"), "text", height=3)
        cs["voies"]           = champ(frame, "Voies d'utilisation", val("voies"), "text", height=3)
        cs["dlc"]             = champ(frame, "Date limite (DLC)", val("dlc"))

    # Propriétés médicinales
    section(frame, "— Propriétés médicinales")
    w_prop   = champ(frame, "Indications / Bénéfices", val("proprietes"),  "text", height=3)
    w_contre = champ(frame, "Contre-indications",      val("contre"),      "text", height=2)
    w_prec   = champ(frame, "Précautions générales",   val("precautions"), "text", height=2)
    if type_ == "he":
        cs["precautions_voies"] = champ(frame, "Précautions par voie", val("precautions_voies"), "text", height=3)

    # Logistique
    section(frame, "— Logistique")
    w_qte   = champ(frame, "Quantité disponible", val("quantite"))
    w_stock = champ(frame, "Lieu de stockage",    val("stockage"))
    w_dist  = champ(frame, "Distributeur",        val("distributeur"))
    w_prix  = champ(frame, "Prix habituel",       val("prix"))
    w_lien  = champ(frame, "Fiche (Word/PDF)",    getattr(plante, "lien", ""), "fichier")
    w_lien._nom_widget = w_nom

    section(frame, "— Notes")
    w_notes = champ(frame, "Notes personnelles", val("notes"), "text", height=3)

    # Boutons
    bot = tk.Frame(win, bg=BG, pady=10)
    bot.pack(fill="x", padx=24)

    def enregistrer():
        nom = lire(w_nom)
        if not nom:
            messagebox.showerror("Erreur", "Le nom est obligatoire.", parent=win)
            return

        if plante:
            obj = plante
        else:
            if type_ == "brute":        obj = PlanteBrute()
            elif type_ == "complement": obj = Complement()
            elif type_ == "he":         obj = HuileEssentielle()
            obj.id = f"{type_}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"

        obj.nom         = nom
        obj.latin       = lire(w_latin)
        obj.famille     = lire(w_fam)
        obj.bio         = lire(w_bio)
        obj.proprietes  = lire(w_prop)
        obj.contre      = lire(w_contre)
        obj.precautions = lire(w_prec)
        obj.quantite    = lire(w_qte)
        obj.stockage    = lire(w_stock)
        obj.distributeur= lire(w_dist)
        obj.prix        = lire(w_prix)
        obj.notes       = lire(w_notes)
        if hasattr(obj, "lien"):
            obj.lien    = lire(w_lien)

        for attr, widget in cs.items():
            setattr(obj, attr, lire(widget))

        if not plante:
            plantes.append(obj)

        sauvegarder(plantes)
        rafraichir()
        win.destroy()

    tk.Button(bot, text="✕ Annuler", command=win.destroy,
              bg=BORDER, fg=FG, font=("Georgia", 10), relief="flat", padx=12, pady=5).pack(side="right", padx=4)
    tk.Button(bot, text="✓ Enregistrer", command=enregistrer,
              bg=VERT, fg="white", font=("Georgia", 10, "bold"),
              relief="flat", padx=12, pady=5, cursor="hand2").pack(side="right", padx=4)

# ══════════════════════════════════════════════════════════════════════════════
# VUE DÉTAIL
# ══════════════════════════════════════════════════════════════════════════════

def ouvrir_detail(p):
    couleur = TYPE_COULEURS.get(p.TYPE, VERT)
    win, frame = faire_fenetre(f"{TYPE_LABELS.get(p.TYPE,'')}  —  {p.nom}", "640px")
    win.geometry("640x680")

    # Recolorer l'en-tête selon le type
    for child in win.winfo_children():
        if isinstance(child, tk.Frame) and child.cget("bg") == VERT:
            child.configure(bg=couleur)
            for w in child.winfo_children():
                try: w.configure(bg=couleur)
                except: pass
            break

    def bloc(label, valeur, couleur_val=FG):
        if not valeur: return
        f = tk.Frame(frame, bg=BG)
        f.pack(fill="x", pady=4)
        tk.Label(f, text=label.upper(), bg=BG, fg=couleur,
                 font=("Georgia", 8, "bold"), anchor="w").pack(fill="x")
        tk.Frame(f, bg=BORDER, height=1).pack(fill="x", pady=2)
        tk.Label(f, text=str(valeur), bg=BG, fg=couleur_val,
                 font=("Georgia", 11), anchor="w", wraplength=560, justify="left").pack(fill="x", padx=4)

    if p.latin:
        tk.Label(frame, text=p.latin, bg=BG, fg=MUTED,
                 font=("Georgia", 11, "italic")).pack(anchor="w", pady=(0, 8))

    # Infos spécifiques en grille
    if p.TYPE == "brute":
        infos = [("Partie", p.partie), ("Origine", p.origine),
                 ("Préparation", p.mode_preparation), ("Température", p.temperature),
                 ("Temps d'infusion", p.temps_infusion), ("Posologie", p.posologie),
                 ("Conditionnement", p.conditionnement)]
    elif p.TYPE == "complement":
        infos = [("Référence", p.reference), ("Partie", p.partie), ("Origine", p.origine),
                 ("Forme", p.forme), ("Dosage", p.dosage), ("Posologie", p.posologie),
                 ("Moment de prise", p.moment_prise), ("Durée de cure", p.duree_cure),
                 ("Conditionnement", p.conditionnement)]
    elif p.TYPE == "he":
        infos = [("Organe", p.organe), ("Origine", p.origine),
                 ("Mode d'obtention", p.mode_obtention), ("Chémotype", p.chemotype), ("DLC", p.dlc)]
    else:
        infos = []

    valides = [(l, v) for l, v in infos if v]
    if valides:
        tk.Frame(frame, bg=BORDER, height=1).pack(fill="x", pady=6)
        g = tk.Frame(frame, bg=BG)
        g.pack(fill="x")
        for i, (lbl, val) in enumerate(valides):
            c = tk.Frame(g, bg=BG)
            c.grid(row=i // 2, column=i % 2, sticky="w", padx=8, pady=2)
            tk.Label(c, text=lbl + " :", bg=BG, fg=couleur, font=("Georgia", 9, "bold")).pack(side="left")
            tk.Label(c, text=val, bg=BG, fg=FG, font=("Georgia", 11)).pack(side="left", padx=4)

    # Champs longs HE
    if p.TYPE == "he":
        bloc("Composition", p.composition)
        bloc("Voies d'utilisation", p.voies)
        bloc("Précautions par voie", p.precautions_voies, BRUN)

    tk.Frame(frame, bg=BORDER, height=1).pack(fill="x", pady=6)
    bloc("Indications / Bénéfices", p.proprietes)
    bloc("⚠ Contre-indications", p.contre, ROUGE)
    bloc("Précautions", p.precautions, BRUN)

    # Logistique
    tk.Frame(frame, bg=BORDER, height=1).pack(fill="x", pady=6)
    log = tk.Frame(frame, bg=BG)
    log.pack(fill="x")
    for i, (lbl, val) in enumerate([("Quantité", p.quantite), ("Stockage", p.stockage),
                                     ("Distributeur", p.distributeur), ("Prix", p.prix)]):
        if val:
            c = tk.Frame(log, bg=BG)
            c.grid(row=i // 2, column=i % 2, sticky="w", padx=8, pady=2)
            tk.Label(c, text=lbl + " :", bg=BG, fg=couleur, font=("Georgia", 9, "bold")).pack(side="left")
            tk.Label(c, text=val, bg=BG, fg=FG, font=("Georgia", 11)).pack(side="left", padx=4)

    # Lien fiche
    lien = getattr(p, "lien", "")
    if lien:
        tk.Frame(frame, bg=BORDER, height=1).pack(fill="x", pady=6)
        lf = tk.Frame(frame, bg=BG)
        lf.pack(fill="x")
        tk.Label(lf, text="Fiche :", bg=BG, fg=couleur, font=("Georgia", 9, "bold")).pack(side="left")
        tk.Label(lf, text=lien, bg=BG, fg=BRUN, font=("Georgia", 10),
                 wraplength=440, justify="left").pack(side="left", padx=6)
        def ouvrir_fichier():
            try: os.startfile(lien)
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible d'ouvrir :\n{e}", parent=win)
        tk.Button(lf, text="📂 Ouvrir", command=ouvrir_fichier, bg=BRUN, fg="white",
                  font=("Georgia", 9), relief="flat", padx=8, cursor="hand2").pack(side="left", padx=4)

    if p.bio:
        tk.Label(frame, text="✅ Biologique", bg=BG, fg=VERT,
                 font=("Georgia", 10, "bold")).pack(anchor="w", pady=4)

    bloc("Notes", p.notes, MUTED)

    # Boutons
    bot = tk.Frame(win, bg=BG, pady=10)
    bot.pack(fill="x", padx=24)
    tk.Button(bot, text="✕ Fermer", command=win.destroy,
              bg=BORDER, fg=FG, font=("Georgia", 10), relief="flat", padx=12, pady=5).pack(side="right", padx=4)
    tk.Button(bot, text="✏ Modifier", command=lambda: [win.destroy(), ouvrir_formulaire(plante=p)],
              bg=couleur, fg="white", font=("Georgia", 10, "bold"),
              relief="flat", padx=12, pady=5, cursor="hand2").pack(side="right", padx=4)

# ══════════════════════════════════════════════════════════════════════════════
# LANCEMENT
# ══════════════════════════════════════════════════════════════════════════════
rafraichir()
root.mainloop()
