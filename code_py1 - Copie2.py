import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import pandas as pd
from scipy.optimize import linprog

def optimize():
    selected_value = prix_combobox.get()
    row_index = prix[prix.iloc[:, 0] == selected_value].index[0]
    C = prix.iloc[row_index, 1:].values.tolist()
    A = ingred.iloc[:, 1:]
    b = nutri.iloc[:, -1]
    n_variables = 21
    bounds = [(0, None)] * n_variables
    result = linprog(C, A_ub=A, b_ub=b, bounds=bounds, method='highs')
    show_result(result, ingred)

def open_database_window(title, data):
    db_window = tk.Toplevel(root)
    db_window.title(title)
    db_window.configure(bg="lightblue")

    text_widget = tk.Text(db_window, bg="lightyellow")
    text_widget.insert(tk.END, data)
    text_widget.pack()

def show_result(result, ingred):
    result_frame.pack(padx=10, pady=10, fill='both', expand=True)
    
    for i in tree.get_children():
        tree.delete(i)
    
    total_mass = simpledialog.askfloat("Masse Totale", "Entrez la masse totale de l'aliment:")

    if total_mass is not None:
        ingredient_masses = [total_mass * x for x in result.x]
        for i, value in enumerate(result.x):
            ingredient_name = ingred.columns[i + 1]
            percentage_value = f"{round(value * 100, 2)}%"
            selected_value = prix_combobox.get()
            row_index = prix[prix.iloc[:, 0] == selected_value].index[0]
            ingred_prix=prix.iloc[row_index,i+1]
            tree.insert("", "end", values=(ingredient_name, f"x{i+1}",f"{ingred_prix}  FCFA",percentage_value, round(ingredient_masses[i], 2)))
            

        fun = f"{round(result.fun, 2)}"
        total_cost = f"{round(result.fun * total_mass,0)}"
        tree.insert("", "end", values=("Fonction Objectif", "", fun, ""))
        tree.insert("", "end", values=("Coût Total", "", total_cost+"  FCFA",""))

def add_new_prix():
    new_entry = {}
    prix_columns = prix.columns.tolist()
    for col in prix_columns:
        value = simpledialog.askstring("Nouvelle Entrée", f"Entrez la valeur pour {col}:")
        if not value:  # Vérifier si la valeur est vide
            messagebox.showerror("Erreur", f"La valeur pour {col} ne peut pas être vide. Ajout annulé.")
            return
        new_entry[col] = value

    prix.loc[len(prix)] = new_entry
    prix.to_excel("data\BASE1_prix.xlsx", index=False)
    messagebox.showinfo("Succès", "Nouvelle entrée ajoutée avec succès!")
    update_prix_combobox()

def update_prix_combobox():
    prix_combobox['values'] = prix.iloc[:, 0].tolist()

root = tk.Tk()
root.title("Optimisation")
root.configure(bg="blue")

# Lecture des fichiers
prix = pd.read_excel("data\BASE1_prix.xlsx")
ingred = pd.read_excel("data\BASE1_ingred.xlsx")
nutri = pd.read_excel("data\BASE1_nutri.xlsx")
incor_matier = pd.read_excel("data\BASE1_incor_matier.xlsx")

# Frame de sélection de période
selection_frame = tk.Frame(root, bg="blue")
selection_frame.pack(padx=20, pady=20)

prix_combobox_label = tk.Label(selection_frame, text="Choisissez une période :", bg="blue", fg="white", font=('Arial', 12, 'bold'))
prix_combobox_label.pack(padx=20, pady=5)

prix_combobox = ttk.Combobox(selection_frame, values=prix.iloc[:, 0].tolist())
prix_combobox.set(prix.iloc[0, 0])
prix_combobox.pack(padx=20, pady=10)

# Frame des boutons
button_frame = tk.Frame(root, bg="blue")
button_frame.pack(padx=20, pady=20, anchor='w')

style = ttk.Style()
style.configure('TButton', padding=6, font=('Arial', 12))
style.configure('TButtonColored.TButton', background='#4CAF50', foreground='white')
style.map('TButtonColored.TButton', background=[('active', '#45a049')])

optimize_btn = ttk.Button(button_frame, text="Optimiser", command=optimize, style='TButtonColored.TButton')
optimize_btn.grid(row=0, column=2, padx=10, pady=10, sticky='w')

add_prix_btn = ttk.Button(button_frame, text="Ajouter une Nouvelle Entrée Prix", command=add_new_prix, style='TButtonColored.TButton')
add_prix_btn.grid(row=1, column=2, padx=10, pady=10, sticky='w')

open_prix_btn = ttk.Button(button_frame, text="Voir la base des prix", command=lambda: open_database_window("Base de données des prix", pd.read_excel("BASE1_prix.xlsx")), style='TButtonColored.TButton')
open_prix_btn.grid(row=0, column=3, padx=10, pady=10, sticky='w')

open_ingred_btn = ttk.Button(button_frame, text="Voir la base des ingrédients", command=lambda: open_database_window("Base de données des ingrédients", pd.read_excel("BASE1_ingred.xlsx")), style='TButtonColored.TButton')
open_ingred_btn.grid(row=1, column=3, padx=10, pady=10, sticky='w')

open_nutri_btn = ttk.Button(button_frame, text="Voir la base nutritionnelle", command=lambda: open_database_window("Base de données nutritionnelles", pd.read_excel("BASE1_nutri.xlsx")), style='TButtonColored.TButton')
open_nutri_btn.grid(row=0, column=4, padx=10, pady=10, sticky='w')

open_incor_matier_btn = ttk.Button(button_frame, text="Voir la base des ingrédients matières", command=lambda: open_database_window("Base de données des ingrédients matières", pd.read_excel("BASE1_incor_matier.xlsx")), style='TButtonColored.TButton')
open_incor_matier_btn.grid(row=1, column=4, padx=10, pady=10, sticky='w')

quit_btn = ttk.Button(button_frame, text="Quitter", command=root.quit, style='TButtonColored.TButton')
quit_btn.grid(row=1, column=5, padx=10, pady=10, sticky='w')

# Frame des résultats
result_frame = tk.Frame(root, bg="blue")
result_frame.pack_forget()

tree = ttk.Treeview(result_frame, columns=("Ingrédients", "Variable","Prix", "Valeur", "Masse (g)"), show="headings")
tree.heading("Ingrédients", text="Ingrédients")
tree.heading("Variable", text="Variable")
tree.heading("Prix", text="Prix")
tree.heading("Valeur", text="Valeur")
tree.heading("Masse (g)", text="Masse (g)")
tree.pack(padx=10, pady=10, fill='both', expand=True)

for col in tree["columns"]:
    tree.heading(col, text=col, anchor=tk.CENTER)
    tree.column(col, anchor=tk.CENTER)
    tree.heading(col, text=col, command=lambda _col=col: tree_sort_column(tree, _col))

root.geometry("500x600")
root.mainloop()
