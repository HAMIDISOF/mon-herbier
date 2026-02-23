import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os

# ── Fichier de données ──────────────────────────────────────────────────────
FICHIER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "herbier_data.json")

def charger():
    if os.path.exists(FICHIER):
        with open(FICHIER, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def sauvegarder(data):
    with open(FICHIER, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ── Données globales ────────────────────────────────────────────────────────
plantes = charger()

# ── Couleurs & styles ───────────────────────────────────────────────────────
BG       = "#f5f0e8"
PAPER    = "#fdf8f0"
VERT     = "#4a7a35"
VERT2    = "#2d5a1e"
BRUN     = "#8b6f3e"
MUTED    = "#7a6d5a"
BORDER   = "#c4b99a"
ROUGE    = "#8b3a2a"
FG       = "#2c2416"

# ── Fenêtre principale ──────────────────────────────────────────────────────
root = tk.Tk()
root.title("🌿 Mon Herbier")
root.geometry("1100x700")
root.configure(bg=BG)
root.minsize(800, 500)

# ── Style ttk ───────────────────────────────────────────────────────────────
style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview",
    background=PAPER, fieldbackground=PAPER, foreground=FG,
    rowheight=28, font=("Georgia", 11), borderwidth=0)
style.configure("Treeview.Heading",
    background=VERT, foreground="white", font=("Georgia", 11, "bold"), relief="flat")
style.map("Treeview", background=[("selected", VERT)], foreground=[("selected", "white")])
style.configure("TScrollbar", background=BORDER, troughcolor=BG)

# ═══════════════════════════════════════════════════════════════════════════
# BARRE DU HAUT
# ═══════════════════════════════════════════════════════════════════════════
top_bar = tk.Frame(root, bg=VERT, pady=12)
top_bar.pack(fill="x")

tk.Label(top_bar, text="🌿 Mon Herbier", bg=VERT, fg="white",
         font=("Georgia", 18, "bold")).pack(side="left", padx=20)
tk.Label(top_bar, text="Carnet de plantes médicinales", bg=VERT, fg="#c8dfc0",
         font=("Georgia", 10, "italic")).pack(side="left")

tk.Button(top_bar, text="+ Nouvelle plante", bg=PAPER, fg=VERT2,
          font=("Georgia", 10, "bold"), relief="flat", padx=12, pady=4,
          cursor="hand2", command=lambda: ouvrir_formulaire()).pack(side="right", padx=8)

# ═══════════════════════════════════════════════════════════════════════════
# BARRE DE RECHERCHE
# ═══════════════════════════════════════════════════════════════════════════
search_bar = tk.Frame(root, bg=BG, pady=10)
search_bar.pack(fill="x", padx=20)

tk.Label(search_bar, text="🔍", bg=BG, font=("Georgia", 12)).pack(side="left")

search_var = tk.StringVar()
search_entry = tk.Entry(search_bar, textvariable=search_var, font=("Georgia", 12),
                        bg=PAPER, fg=FG, relief="solid", bd=1, width=35)
search_entry.pack(side="left", padx=8, ipady=4)
search_var.trace_add("write", lambda *a: rafraichir())

tk.Label(search_bar, text="Partie :", bg=BG, fg=MUTED, font=("Georgia", 10)).pack(side="left", padx=(20,4))
partie_var = tk.StringVar(value="Toutes")
parties = ["Toutes", "Fleur", "Feuille", "Racine", "Écorce", "Graine", "Fruit", "Huile essentielle", "Plante entière"]
partie_cb = ttk.Combobox(search_bar, textvariable=partie_var, values=parties,
                          state="readonly", width=18, font=("Georgia", 10))
partie_cb.pack(side="left")
partie_cb.bind("<<ComboboxSelected>>", lambda e: rafraichir())

stats_label = tk.Label(search_bar, text="", bg=BG, fg=MUTED, font=("Georgia", 9, "italic"))
stats_label.pack(side="right", padx=10)

# ═══════════════════════════════════════════════════════════════════════════
# TABLEAU PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════
main_frame = tk.Frame(root, bg=BG)
main_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))

colonnes = ("nom", "latin", "partie", "maladies", "contre", "quantite", "distributeur", "prix")
entetes  = ("Nom", "Nom latin", "Partie", "Indications", "Contre-indications", "Quantité", "Distributeur", "Prix")
largeurs = (140, 160, 110, 220, 180, 90, 140, 80)

tree = ttk.Treeview(main_frame, columns=colonnes, show="headings", selectmode="browse")
for col, ent, larg in zip(colonnes, entetes, largeurs):
    tree.heading(col, text=ent, command=lambda c=col: trier(c))
    tree.column(col, width=larg, minwidth=60)

scroll_y = ttk.Scrollbar(main_frame, orient="vertical", command=tree.yview)
scroll_x = ttk.Scrollbar(main_frame, orient="horizontal", command=tree.xview)
tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

tree.grid(row=0, column=0, sticky="nsew")
scroll_y.grid(row=0, column=1, sticky="ns")
scroll_x.grid(row=1, column=0, sticky="ew")
main_frame.rowconfigure(0, weight=1)
main_frame.columnconfigure(0, weight=1)

tree.tag_configure("pair",   background="#f0ece0")
tree.tag_configure("impair", background=PAPER)

# ═══════════════════════════════════════════════════════════════════════════
# BARRE D'ACTIONS BAS
# ═══════════════════════════════════════════════════════════════════════════
tree.bind("<Double-1>", lambda e: voir_selection())

# ═══════════════════════════════════════════════════════════════════════════
# LOGIQUE
# ═══════════════════════════════════════════════════════════════════════════
tri_col = None
tri_inverse = False

def trier(col):
    global tri_col, tri_inverse
    if tri_col == col:
        tri_inverse = not tri_inverse
    else:
        tri_col = col
        tri_inverse = False
    rafraichir()

def plante_correspond(p, q, partie):
    if partie != "Toutes" and p.get("partie", "") != partie:
        return False
    if q:
        champs = " ".join([p.get(c, "") for c in ("nom","latin","maladies","contre","precautions","distributeur","notes","stockage")])
        if q.lower() not in champs.lower():
            return False
    return True

def rafraichir():
    q = search_var.get()
    partie = partie_var.get()
    filtrees = [p for p in plantes if plante_correspond(p, q, partie)]

    if tri_col:
        filtrees.sort(key=lambda p: p.get(tri_col, "").lower(), reverse=tri_inverse)

    tree.delete(*tree.get_children())
    for i, p in enumerate(filtrees):
        tag = "pair" if i % 2 == 0 else "impair"
        tree.insert("", "end", iid=p["id"], tags=(tag,), values=(
            p.get("nom",""), p.get("latin",""), p.get("partie",""),
            p.get("maladies",""), p.get("contre",""),
            p.get("quantite",""), p.get("distributeur",""), p.get("prix","")
        ))
    stats_label.config(text=f"{len(filtrees)} / {len(plantes)} plante(s)")

def get_selected():
    sel = tree.selection()
    if not sel:
        messagebox.showinfo("Info", "Sélectionnez d'abord une plante dans la liste.")
        return None
    pid = sel[0]
    return next((p for p in plantes if p["id"] == pid), None)

def modifier_selection():
    p = get_selected()
    if p:
        ouvrir_formulaire(p)

def supprimer_selection():
    p = get_selected()
    if not p:
        return
    if messagebox.askyesno("Confirmer", f"Supprimer « {p['nom']} » ?"):
        plantes.remove(p)
        sauvegarder(plantes)
        rafraichir()

def voir_selection():
    p = get_selected()
    if p:
        ouvrir_detail(p)

def exporter():
    chemin = filedialog.asksaveasfilename(
        defaultextension=".json", filetypes=[("JSON", "*.json")],
        initialfile="herbier_export.json", title="Exporter les données")
    if chemin:
        with open(chemin, "w", encoding="utf-8") as f:
            json.dump(plantes, f, ensure_ascii=False, indent=2)
        messagebox.showinfo("Export", "Données exportées avec succès !")

def importer():
    global plantes
    chemin = filedialog.askopenfilename(filetypes=[("JSON", "*.json")], title="Importer un fichier JSON")
    if chemin:
        with open(chemin, "r", encoding="utf-8") as f:
            data = json.load(f)
        if messagebox.askyesno("Importer", f"Importer {len(data)} plante(s) ? Cela remplacera les données actuelles."):
            plantes = data
            sauvegarder(plantes)
            rafraichir()

# ═══════════════════════════════════════════════════════════════════════════
# FORMULAIRE AJOUT / MODIFICATION
# ═══════════════════════════════════════════════════════════════════════════
def ouvrir_formulaire(plante=None):
    win = tk.Toplevel(root)
    win.title("Nouvelle plante" if not plante else "Modifier — " + plante.get("nom",""))
    win.geometry("680x720")
    win.configure(bg=BG)
    win.grab_set()

    # En-tête
    tk.Frame(win, bg=VERT, height=50).pack(fill="x")
    header = win.children[list(win.children)[-1]]
    tk.Label(header, text="🌿 " + ("Nouvelle plante" if not plante else "Modifier la plante"),
             bg=VERT, fg="white", font=("Georgia", 14, "bold")).place(x=16, y=12)

    # Scrollable frame
    canvas = tk.Canvas(win, bg=BG, highlightthickness=0)
    sb = ttk.Scrollbar(win, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=sb.set)
    sb.pack(side="right", fill="y")
    canvas.pack(fill="both", expand=True)

    frame = tk.Frame(canvas, bg=BG, padx=24, pady=16)
    cw = canvas.create_window((0,0), window=frame, anchor="nw")

    def on_configure(e):
        canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.itemconfig(cw, width=canvas.winfo_width())
    frame.bind("<Configure>", on_configure)
    canvas.bind("<Configure>", on_configure)
    canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))

    champs = {}

    def ligne(parent, label, key, widget_type="entry", options=None, height=3):
        row = tk.Frame(parent, bg=BG)
        row.pack(fill="x", pady=4)
        tk.Label(row, text=label, bg=BG, fg=VERT2, font=("Georgia", 9, "bold"),
                 width=22, anchor="w").pack(side="left")
        if widget_type == "entry":
            w = tk.Entry(row, font=("Georgia", 11), bg=PAPER, fg=FG, relief="solid", bd=1)
            w.pack(side="left", fill="x", expand=True, ipady=3)
        elif widget_type == "combo":
            v = tk.StringVar()
            w = ttk.Combobox(row, textvariable=v, values=options or [], state="readonly",
                             font=("Georgia", 11), width=25)
            w.pack(side="left")
            champs[key] = v
            if plante and plante.get(key):
                v.set(plante[key])
            return
        elif widget_type == "text":
            w = tk.Text(row, font=("Georgia", 11), bg=PAPER, fg=FG, relief="solid",
                        bd=1, height=height, wrap="word")
            w.pack(side="left", fill="x", expand=True)
        elif widget_type == "fichier":
            sub = tk.Frame(row, bg=BG)
            sub.pack(side="left", fill="x", expand=True)
            w = tk.Entry(sub, font=("Georgia", 10), bg=PAPER, fg=FG, relief="solid", bd=1)
            w.pack(side="left", fill="x", expand=True, ipady=3)
            def parcourir(entry=w):
                chemin = filedialog.askopenfilename(
                    title="Choisir la fiche",
                    filetypes=[("Documents", "*.pdf *.docx *.doc"), ("Tous", "*.*")])
                if chemin:
                    entry.delete(0, "end")
                    entry.insert(0, chemin)
                    # Remplir le nom depuis le titre du fichier si le champ est vide
                    nom_widget = champs.get("nom")
                    if nom_widget and not nom_widget.get().strip():
                        nom_fichier = os.path.splitext(os.path.basename(chemin))[0]
                        nom_widget.delete(0, "end")
                        nom_widget.insert(0, nom_fichier)
            tk.Button(sub, text="📂 Parcourir", command=parcourir, bg=BRUN, fg="white",
                      font=("Georgia", 9), relief="flat", padx=8, cursor="hand2").pack(side="left", padx=6)
            champs[key] = w
            if plante and plante.get(key):
                w.insert(0, plante[key])
            return

        champs[key] = w
        if plante and plante.get(key):
            if widget_type == "text":
                w.insert("1.0", plante[key])
            else:
                w.insert(0, plante[key])

    # Séparateur section
    def section(titre):
        f = tk.Frame(frame, bg=BG)
        f.pack(fill="x", pady=(12,4))
        tk.Label(f, text=titre, bg=BG, fg=VERT, font=("Georgia", 11, "bold italic")).pack(side="left")
        tk.Frame(f, bg=BORDER, height=1).pack(side="left", fill="x", expand=True, padx=8, pady=6)

    section("— Identification")
    ligne(frame, "Nom commun *",    "nom")
    ligne(frame, "Nom latin",       "latin")
    ligne(frame, "Partie utilisée", "partie", "combo",
          ["Fleur","Feuille","Racine","Écorce","Graine","Fruit","Huile essentielle","Plante entière"])

    section("— Propriétés médicinales")
    ligne(frame, "Maladies / maux soulagés", "maladies", "text", height=3)
    ligne(frame, "Contre-indications",        "contre",   "text", height=2)
    ligne(frame, "Précautions d'usage",       "precautions", "text", height=2)

    section("— Logistique")
    ligne(frame, "Quantité disponible", "quantite")
    ligne(frame, "Lieu de stockage",    "stockage")
    ligne(frame, "Distributeur",        "distributeur")
    ligne(frame, "Prix habituel",       "prix")
    ligne(frame, "Fiche (Word/PDF)",    "lien", "fichier")

    section("— Notes")
    ligne(frame, "Notes personnelles", "notes", "text", height=3)

    # Boutons
    bot = tk.Frame(win, bg=BG, pady=10)
    bot.pack(fill="x", padx=24)

    def get_val(key):
        w = champs[key]
        if isinstance(w, tk.Text):
            return w.get("1.0", "end").strip()
        elif isinstance(w, tk.StringVar):
            return w.get().strip()
        else:
            return w.get().strip()

    def enregistrer():
        nom = get_val("nom")
        if not nom:
            messagebox.showerror("Erreur", "Le nom de la plante est obligatoire.", parent=win)
            return
        p = {
            "id": plante["id"] if plante else str(len(plantes) + 1) + "_" + nom[:8].replace(" ",""),
            "nom": nom,
            "latin": get_val("latin"),
            "partie": get_val("partie"),
            "maladies": get_val("maladies"),
            "contre": get_val("contre"),
            "precautions": get_val("precautions"),
            "quantite": get_val("quantite"),
            "stockage": get_val("stockage"),
            "distributeur": get_val("distributeur"),
            "prix": get_val("prix"),
            "lien": get_val("lien"),
            "notes": get_val("notes"),
        }
        if plante:
            idx = plantes.index(plante)
            plantes[idx] = p
        else:
            plantes.append(p)
        sauvegarder(plantes)
        rafraichir()
        win.destroy()

    tk.Button(bot, text="✕ Annuler", command=win.destroy, bg=BORDER, fg=FG,
              font=("Georgia", 10), relief="flat", padx=12, pady=5).pack(side="right", padx=4)
    tk.Button(bot, text="✓ Enregistrer", command=enregistrer, bg=VERT, fg="white",
              font=("Georgia", 10, "bold"), relief="flat", padx=12, pady=5,
              cursor="hand2").pack(side="right", padx=4)

# ═══════════════════════════════════════════════════════════════════════════
# VUE DÉTAIL
# ═══════════════════════════════════════════════════════════════════════════
def ouvrir_detail(p):
    win = tk.Toplevel(root)
    win.title("Fiche — " + p.get("nom",""))
    win.geometry("600x650")
    win.configure(bg=BG)
    win.grab_set()

    tk.Frame(win, bg=VERT, height=50).pack(fill="x")
    header = win.children[list(win.children)[-1]]
    nom_txt = p.get("nom","") + ("  —  " + p.get("partie","") if p.get("partie") else "")
    tk.Label(header, text="🌿 " + nom_txt, bg=VERT, fg="white",
             font=("Georgia", 14, "bold")).place(x=16, y=12)

    canvas = tk.Canvas(win, bg=BG, highlightthickness=0)
    sb = ttk.Scrollbar(win, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=sb.set)
    sb.pack(side="right", fill="y")
    canvas.pack(fill="both", expand=True)

    frame = tk.Frame(canvas, bg=BG, padx=24, pady=16)
    cw = canvas.create_window((0,0), window=frame, anchor="nw")
    def on_conf(e):
        canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.itemconfig(cw, width=canvas.winfo_width())
    frame.bind("<Configure>", on_conf)
    canvas.bind("<Configure>", on_conf)

    def bloc(label, valeur, couleur_val=FG):
        if not valeur:
            return
        f = tk.Frame(frame, bg=BG)
        f.pack(fill="x", pady=5)
        tk.Label(f, text=label.upper(), bg=BG, fg=VERT, font=("Georgia", 8, "bold"),
                 anchor="w").pack(fill="x")
        tk.Frame(f, bg=BORDER, height=1).pack(fill="x", pady=2)
        tk.Label(f, text=valeur, bg=BG, fg=couleur_val, font=("Georgia", 11),
                 anchor="w", wraplength=520, justify="left").pack(fill="x", padx=4)

    if p.get("latin"):
        tk.Label(frame, text=p["latin"], bg=BG, fg=MUTED,
                 font=("Georgia", 11, "italic")).pack(anchor="w", pady=(0,10))

    bloc("Indications / Maladies soulagées", p.get("maladies"))
    bloc("⚠ Contre-indications", p.get("contre"), ROUGE)
    bloc("Précautions d'usage", p.get("precautions"), BRUN)

    # Ligne logistique
    tk.Frame(frame, bg=BORDER, height=1).pack(fill="x", pady=8)
    grid = tk.Frame(frame, bg=BG)
    grid.pack(fill="x")
    infos = [("Quantité", p.get("quantite")), ("Stockage", p.get("stockage")),
             ("Distributeur", p.get("distributeur")), ("Prix", p.get("prix"))]
    for i, (lbl, val) in enumerate(infos):
        if val:
            c = tk.Frame(grid, bg=BG)
            c.grid(row=i//2, column=i%2, sticky="w", padx=8, pady=3)
            tk.Label(c, text=lbl + " :", bg=BG, fg=VERT, font=("Georgia", 9, "bold")).pack(side="left")
            tk.Label(c, text=val, bg=BG, fg=FG, font=("Georgia", 11)).pack(side="left", padx=4)

    if p.get("lien"):
        tk.Frame(frame, bg=BORDER, height=1).pack(fill="x", pady=8)
        lf = tk.Frame(frame, bg=BG)
        lf.pack(fill="x")
        tk.Label(lf, text="Fiche :", bg=BG, fg=VERT, font=("Georgia", 9, "bold")).pack(side="left")
        tk.Label(lf, text=p["lien"], bg=BG, fg=BRUN, font=("Georgia", 10),
                 wraplength=420, justify="left").pack(side="left", padx=6)
        def ouvrir_fichier():
            import subprocess
            try:
                os.startfile(p["lien"])
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible d'ouvrir le fichier :\n{e}", parent=win)
        tk.Button(lf, text="📂 Ouvrir", command=ouvrir_fichier, bg=BRUN, fg="white",
                  font=("Georgia", 9), relief="flat", padx=8, cursor="hand2").pack(side="left", padx=4)

    bloc("Notes personnelles", p.get("notes"), MUTED)

    # Boutons
    bot = tk.Frame(win, bg=BG, pady=10)
    bot.pack(fill="x", padx=24)
    tk.Button(bot, text="✕ Fermer", command=win.destroy, bg=BORDER, fg=FG,
              font=("Georgia", 10), relief="flat", padx=12, pady=5).pack(side="right", padx=4)
    tk.Button(bot, text="✏ Modifier", command=lambda: [win.destroy(), ouvrir_formulaire(p)],
              bg=VERT, fg="white", font=("Georgia", 10, "bold"), relief="flat",
              padx=12, pady=5, cursor="hand2").pack(side="right", padx=4)

# ═══════════════════════════════════════════════════════════════════════════
# BARRE D'ACTIONS BAS (créée ici car nécessite les fonctions définies avant)
# ═══════════════════════════════════════════════════════════════════════════
bot_bar = tk.Frame(root, bg=BG, pady=6)
bot_bar.pack(fill="x", padx=20)

def btn(parent, texte, cmd, couleur=VERT, fg="white"):
    return tk.Button(parent, text=texte, command=cmd, bg=couleur, fg=fg,
                     font=("Georgia", 10), relief="flat", padx=10, pady=4,
                     cursor="hand2", activebackground=VERT2, activeforeground="white")

btn(bot_bar, "✏  Modifier",     modifier_selection).pack(side="left", padx=4)
btn(bot_bar, "👁  Voir fiche",   voir_selection).pack(side="left", padx=4)
btn(bot_bar, "🗑  Supprimer",    supprimer_selection, ROUGE).pack(side="left", padx=4)
btn(bot_bar, "⬇ Exporter JSON", exporter, BRUN).pack(side="right", padx=4)
btn(bot_bar, "⬆ Importer JSON", importer, BRUN).pack(side="right", padx=4)

# ═══════════════════════════════════════════════════════════════════════════
# LANCEMENT
# ═══════════════════════════════════════════════════════════════════════════
rafraichir()
root.mainloop()
