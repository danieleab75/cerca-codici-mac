import os
import sys
import shutil
import json
import tkinter as tk
from tkinter import filedialog, messagebox

FILE_PERCORSI = "percorsi.json"

percorsi_default = {
    "Distribuzioni": r"\\192.168.1.30\Campionario\Documenti\Campionario\distribuzioni",
    "Christmas": r"\\192.168.1.30\Campionario\Documenti\Campionario\christmas"
}

def carica_percorsi():
    if os.path.exists(FILE_PERCORSI):
        with open(FILE_PERCORSI, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        salva_percorsi(percorsi_default)
        return percorsi_default

def salva_percorsi(data):
    with open(FILE_PERCORSI, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def genera_nome_unico(percorso_destinazione):
    base, estensione = os.path.splitext(percorso_destinazione)
    counter = 1
    nuovo_percorso = percorso_destinazione
    while os.path.exists(nuovo_percorso):
        nuovo_percorso = f"{base}_{counter}{estensione}"
        counter += 1
    return nuovo_percorso

def avvia_programma(codici, percorsi_da_usare):
    if not percorsi_da_usare:
        messagebox.showwarning("Attenzione", "Seleziona almeno una cartella.")
        return

    codici = [c.strip() for c in codici.splitlines() if c.strip()]
    if not codici:
        messagebox.showerror("Errore", "Nessun codice valido inserito.")
        return

    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))

    destinazione = os.path.join(base_dir, "Trovati")
    os.makedirs(destinazione, exist_ok=True)
    trovati = []

    for percorso in percorsi_da_usare:
        for root, _, files in os.walk(percorso):
            for file in files:
                for codice in codici:
                    if codice in file:
                        origine = os.path.join(root, file)
                        destinazione_file = genera_nome_unico(os.path.join(destinazione, file))
                        shutil.copy2(origine, destinazione_file)
                        trovati.append(os.path.basename(destinazione_file))
                        break

    messagebox.showinfo("Completato", f"Trovati e copiati {len(trovati)} file nella cartella 'Trovati'.")

def modifica_percorsi():
    percorsi = carica_percorsi()
    finestra = tk.Toplevel()
    finestra.title("Modifica Percorsi")

    voci = {}
    for nome, percorso in percorsi.items():
        label = tk.Label(finestra, text=nome)
        label.pack()
        entry = tk.Entry(finestra, width=50)
        entry.insert(0, percorso)
        entry.pack()
        voci[nome] = entry

    def salva():
        nuovi = {nome: campo.get() for nome, campo in voci.items()}
        salva_percorsi(nuovi)
        messagebox.showinfo("Salvato", "Percorsi aggiornati.")
        finestra.destroy()

    tk.Button(finestra, text="Salva", command=salva).pack(pady=10)

def mostra_interfaccia():
    percorsi = carica_percorsi()

    finestra = tk.Tk()
    finestra.title("Cerca foto ad alta risoluzione")

    tk.Label(finestra, text="Inserisci i codici (uno per riga):").pack(padx=10, pady=5)
    area_testo = tk.Text(finestra, width=50, height=15)
    area_testo.pack(padx=10)
    area_testo.focus_set()

    # Pulsante Importa
    def importa_codici(percorso=None):
        if not percorso:
            percorso = filedialog.askopenfilename(
                title="Seleziona file .txt",
                filetypes=[("File di testo", "*.txt")]
            )
            if not percorso:
                return  # annullato

        try:
            with open(percorso, "r", encoding="utf-8") as f:
                codici = f.read().strip().splitlines()
                for codice in codici:
                    if codice.strip():
                        area_testo.insert(tk.INSERT, codice.strip() + "\n")
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile importare il file:\n{e}")

    frame_bottoni = tk.Frame(finestra)
    frame_bottoni.pack(pady=5)

    tk.Button(frame_bottoni, text="Importa elenco da Pencil", command=lambda: importa_codici("C:/Temp/pencil.txt")).pack(side="left", padx=5)
    tk.Button(frame_bottoni, text="📁 Scegli file .txt", command=importa_codici).pack(side="left", padx=5)

    # Frame per checkbox + modifica percorsi
    frame_superiore = tk.Frame(finestra)
    frame_superiore.pack(pady=10)

    selezioni = {}
    for nome in percorsi:
        var = tk.BooleanVar(value=True)
        cb = tk.Checkbutton(frame_superiore, text=f"Cerca in '{nome}'", variable=var)
        cb.pack(side="left", padx=5)
        selezioni[nome] = var

    btn_modifica = tk.Button(frame_superiore, text="Modifica Percorsi", command=modifica_percorsi)
    btn_modifica.pack(side="left", padx=10)

    def conferma():
        codici_input = area_testo.get("1.0", tk.END)
        selezionati = [p for nome, p in percorsi.items() if selezioni[nome].get()]
        avvia_programma(codici_input, selezionati)

    tk.Button(finestra, text="✅ Conferma e cerca", command=conferma, font=("Arial", 12), bg="#4CAF50", fg="white", height=2, width=25).pack(pady=20)

    finestra.mainloop()

mostra_interfaccia()
