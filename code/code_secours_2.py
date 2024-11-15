#****************************************************************************
# Pour executer étant sur spider , il faut ouvrir le dossier "optimisproj" 
#au niveau de l'onglet projet de spider
#Le Code administrateur de l'application: 1234, cela se trouve aussi dans le document ".txt"
#****************************************************************************


import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import pandas as pd
from scipy.optimize import linprog # type: ignore

# Fonction de confirmation de fermeture
def on_closing():
    if messagebox.askokcancel("Quitter", "Voulez-vous vraiment quitter ?"):
        root.destroy()

# Optimiser
def optimize():
    selected_value = prix_combobox.get()
    row_index = prix[prix.iloc[:, 0] == selected_value].index[0]
    C = prix.iloc[row_index, 1:].values.tolist()
    A = ingred.iloc[:, 1:]
    b = nutri.iloc[:, -1]
    n_variables = 21
    bounds = [(0, None)] * n_variables
    result = linprog(C, A_ub=A, b_ub=b, bounds=bounds, method='simplex')
    show_result(result, ingred)

# Ouvrir la base
def open_database_window(title, data):
    db_window = tk.Toplevel(root)
    db_window.title(title)
    db_window.configure(bg="lightblue")
    db_window.iconbitmap("Capt.ico")

    # Canevas pour le défilement
    canvas = tk.Canvas(db_window, bg="lightyellow")
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Barre de défilement vertical
    v_scrollbar = ttk.Scrollbar(db_window, orient=tk.VERTICAL, command=canvas.yview)
    v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # Barre de défilement horizontal
    h_scrollbar = ttk.Scrollbar(db_window, orient=tk.HORIZONTAL, command=canvas.xview)
    h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
    
    # Cadre pour contenir les données
    frame = tk.Frame(canvas, bg="lightyellow")
    canvas.create_window((0, 0), window=frame, anchor='nw')

    # Insérer les en-têtes de colonnes
    for col_num, col_name in enumerate(data.columns):
        label = tk.Label(frame, text=col_name, bg="lightblue", relief=tk.RAISED, width=15, anchor='w')
        label.grid(row=0, column=col_num, padx=1, pady=1)

    # Insérer les données
    for row_num, row_data in data.iterrows():
        for col_num, cell_value in enumerate(row_data):
            label = tk.Label(frame, text=cell_value, bg="lightyellow", relief=tk.RAISED, width=15, anchor='w')
            label.grid(row=row_num + 1, column=col_num, padx=1, pady=1)

    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
        
    
    frame.bind("<Configure>", on_frame_configure)
    
    canvas.update_idletasks()
    
    close_btn = ttk.Button(db_window, text="Fermer", command=db_window.destroy)
    close_btn.pack(pady=10)

# Voir le résultat
def show_result(result, ingred):
    result_frame.pack(padx=10, pady=10, fill='both', expand=True)
    
    for i in tree.get_children():
        tree.delete(i)
    
    total_mass = simpledialog.askfloat("Masse Totale", "Entrez la masse totale de l'aliment:")

    if total_mass is not None:
        ingredient_masses = [total_mass * x for x in result.x]
        for i, value in enumerate(result.x):
            ingredient_name = ingred.columns[i + 1]
            percentage_value = f"{round(value * 100, 2)} %"
            selected_value = prix_combobox.get()
            row_index = prix[prix.iloc[:, 0] == selected_value].index[0]
            ingred_prix = prix.iloc[row_index, i+1]
            tree.insert("", "end", values=(ingredient_name, f"x{i+1}", f"{ingred_prix} FCFA", percentage_value, round(ingredient_masses[i], 2)))

        total_cost = f"{round(result.fun * total_mass, 0)}"
        tree.insert("", "end", values=("Coût Total", "", total_cost + " FCFA", ""))

# Ajouter de nouveaux prix
def add_new_prix():
    root.iconbitmap("Capt.ico")
    new_entry = {}
    prix_columns = prix.columns.tolist()
    for col in prix_columns:
        value = simpledialog.askstring("Nouvelle Entrée", f"Entrez la valeur pour {col}:")
        if not value:  # Vérifier si la valeur est vide
            messagebox.showerror("Erreur", f"La valeur pour {col} ne peut pas être vide. Ajout annulé.")
            return
        new_entry[col] = value

    prix.loc[len(prix)] = new_entry
    prix.to_excel("BASE1_prix.xlsx", index=False)
    messagebox.showinfo("Succès", "Nouvelle entrée ajoutée avec succès!")
    update_prix_combobox()

# Réinitialisation des prix
def update_prix_combobox():
    prix_combobox['values'] = prix.iloc[:, 0].tolist()

def create_custom_treeview_header(treeview):
    canvas = tk.Canvas(result_frame, height=30, bg='blue', bd=0, highlightthickness=0)
    canvas.pack(fill='x')
    
    columns = treeview["columns"]
    column_widths = [treeview.column(col, 'width') for col in columns]
    column_names = [treeview.heading(col, 'text') for col in columns]
    
    for i, (name, width) in enumerate(zip(column_names, column_widths)):
        canvas.create_rectangle(i*width, 0, (i+1)*width, 30, fill='blue', outline='blue')
        canvas.create_text((i*width) + width/2, 15, text=name, fill='white', font=('Arial', 10, 'bold'))

def show_about_window():
    about_window = tk.Toplevel(root)
    about_window.title("À propos")
    about_window.configure(bg="lightblue")

    about_text = (
        "Application d'Optimisation\n\n"
        "Thème: FORMULATION DES ALIMENTS COMPLETS POUR VOLAILLE DE LA AdNaFaSie Aliment\n\n"
        "Cette application permet d'optimiser le coût des ingrédients\n\n"
        "en fonction des prix des nutriments, des ingrédients disponibles\n\n"
        "et de la masse d'aliments à formuler.\n\n"
        "Elle utilise la programmation linéaire (Méthode Simplexe) pour trouver la solution optimale.\n\n"
        "Elle a été développée dans le cadre du projet d'optimisation sous la supervision de:\n\n"
        "M.DIOP, Enseignant à L'ENSAE Pierre Ndiaye\n\n"
        "Développée par : Adam Alassane Ibrahim, Fallou NGom, Lamine Ndao et Sié Rachid Traoré\n\n"
        "© 2024 Elèves ingénieurs statisticiens économistes\n\n"
        "Ecole Nationale de la Statistique et de l'Analyse Economique Pierre Ndiaye. Tous droits réservés.\n\n"
    )
    
    label = tk.Label(about_window, text=about_text, bg="white", font=('Arial', 17), padx=20, pady=20)
    label.pack(padx=10, pady=10)

    close_btn = ttk.Button(about_window, text="Fermer", command=about_window.destroy)
    close_btn.pack(pady=10)

def check_code():
    code = code_entry.get()
    if code == "1234":  # Remplacez par le code réel de l'administrateur
        login_window.destroy()
        show_main_window()
    else:
        messagebox.showerror("Erreur", "Code incorrect. Veuillez réessayer.")

def show_main_window():
    global root, prix, ingred, nutri, incor_matier, prix_combobox, tree, result_frame

    root = tk.Tk()
    root.title("FeedOptiMax")
    root.configure(bg="green")
    root.iconbitmap("Capt.ico")

    # Configurer la fonction de fermeture
    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Lecture des fichiers
    try:
        prix = pd.read_excel("BASE1_prix.xlsx")
        ingred = pd.read_excel("BASE1_ingred.xlsx")
        nutri = pd.read_excel("BASE1_nutri.xlsx")
        incor_matier = pd.read_excel("BASE1_incor_matier.xlsx")
    except FileNotFoundError as e:
        messagebox.showerror("Erreur", f"Fichier manquant : {e.filename}")
        root.destroy()

    # Frame de sélection de période
    selection_frame = tk.Frame(root, bg="yellow")
    selection_frame.pack(padx=20, pady=10)

    prix_combobox_label = tk.Label(selection_frame, text="Choisissez une période :", bg="blue", fg="white", font=('Arial', 12, 'bold'))
    prix_combobox_label.grid(row=0, column=0, padx=5, pady=5, sticky='w')

    prix_combobox = ttk.Combobox(selection_frame, values=prix.iloc[:, 0].tolist())
    prix_combobox.set(prix.iloc[0, 0])
    prix_combobox.grid(row=0, column=1, padx=5, pady=5, sticky='w')

    # Frame des boutons
    button_frame = tk.Frame(root, bg="red")
    button_frame.pack(padx=35, pady=15, anchor='w')

    style = ttk.Style()
    style.configure('TButton', padding=6, font=('Arial', 15))
    style.configure('TButtonColored.TButton', background='#4CAF50', foreground='black')
    style.map('TButtonColored.TButton', background=[('active', '#45a049')])

    width_button = 25
    optimize_btn = ttk.Button(button_frame, text="Optimiser", command=optimize, style='TButtonColored.TButton', width=width_button)
    optimize_btn.grid(row=0, column=0, padx=5, pady=5, sticky='w')

    add_prix_btn = ttk.Button(button_frame, text="Ajouter une Nouvelle Entrée Prix", command=add_new_prix, style='TButtonColored.TButton', width=width_button)
    add_prix_btn.grid(row=1, column=0, padx=5, pady=5, sticky='w')

    open_prix_btn = ttk.Button(button_frame, text="Voir la base des prix", command=lambda: open_database_window("Base de données des prix", prix), style='TButtonColored.TButton', width=width_button)
    open_prix_btn.grid(row=0, column=1, padx=5, pady=5, sticky='w')

    open_ingred_btn = ttk.Button(button_frame, text="Voir la base des ingrédients", command=lambda: open_database_window("Base de données des ingrédients", ingred), style='TButtonColored.TButton', width=width_button)
    open_ingred_btn.grid(row=1, column=1, padx=5, pady=5, sticky='w')

    open_nutri_btn = ttk.Button(button_frame, text="Voir la base nutritionnelle", command=lambda: open_database_window("Base de données nutritionnelles", nutri), style='TButtonColored.TButton', width=width_button)
    open_nutri_btn.grid(row=0, column=2, padx=5, pady=5, sticky='w')

    open_incor_matier_btn = ttk.Button(button_frame, text="Voir la base des ingrédients matières", command=lambda: open_database_window("Base de données des ingrédients matières", incor_matier), style='TButtonColored.TButton', width=width_button)
    open_incor_matier_btn.grid(row=1, column=2, padx=5, pady=5, sticky='w')

    about_btn = ttk.Button(button_frame, text="Help", command=show_about_window, style='TButtonColored.TButton', width=width_button)
    about_btn.grid(row=0, column=3, padx=5, pady=5, sticky='w')

    quit_btn = ttk.Button(button_frame, text="Quitter", command=on_closing, style='TButtonColored.TButton', width=width_button)
    quit_btn.grid(row=1, column=3, padx=5, pady=5, sticky='w')

    # Frame des résultats
    result_frame = tk.Frame(root, bg="blue")
    result_frame.pack_forget()

    tree = ttk.Treeview(result_frame, columns=("Ingrédients", "Variable", "Prix", "Valeur", "Masse (kg)"), show="headings")
    tree.heading("Ingrédients", text="Ingrédients")
    tree.heading("Variable", text="Variable")
    tree.heading("Prix", text="Prix")
    tree.heading("Valeur", text="Valeur")
    tree.heading("Masse (kg)", text="Masse (kg)")
    tree.pack(padx=10, pady=10, fill='both', expand=True)

    for col in tree["columns"]:
        tree.heading(col, text=col, anchor=tk.CENTER)
        tree.column(col, anchor=tk.CENTER, width=100)

    create_custom_treeview_header(tree)

    root.geometry("700x700")
    root.mainloop()

# Fenêtre de connexion
login_window = tk.Tk()
login_window.title("CONNEXION ADMINISTRATEUR")
login_window.configure(bg="lightgreen")

# Définir les dimensions de la fenêtre de connexion
window_width = 700
window_height = 700

# Obtenir les dimensions de l'écran
screen_width = login_window.winfo_screenwidth()
screen_height = login_window.winfo_screenheight()

# Calculer la position pour centrer la fenêtre
x = (screen_width // 2) - (window_width // 5)
y = (screen_height // 2) - (window_height // 5)

# Appliquer les dimensions et la position à la fenêtre
login_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
login_window.iconbitmap("Capt.ico")

login_label = tk.Label(login_window, text="Veuillez entrer le code administrateur :", bg="lightblue",fg="black", font=('Arial', 18))
login_label.pack(padx=10, pady=10)

code_entry = tk.Entry(login_window, show='*', font=('Arial', 16))
code_entry.pack(padx=10, pady=10)

login_button = ttk.Button(login_window, text="Connexion", command=check_code)
login_button.pack(padx=20, pady=20)

login_window.mainloop()
