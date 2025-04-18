# utils.py

import pandas as pd
import streamlit as st

# Opzioni per selezione di statistiche 
optionsRecord = [
    ("Vittorie", "V"),
    ("Pareggi", "N"),
    ("Sconfitte", "P"),
    ("Gol fatti", "Gf"),
    ("Gol subiti", "Gs"),
    ("Punti", "Pt."),
    ("Punti Totali", "Pt. Totali")
]

# Anni disponibili per la selezione
optionsYear = [
    '16-17', '17-18', '18-19', '19-20', '20-21', '21-22', '22-23', '23-24'
]

# ===============================

def carica_dati():
    try:
        file_excel = pd.ExcelFile("FsStats.xlsx")
        dati = []

        for anno in file_excel.sheet_names:
            try:
                df = file_excel.parse(anno)
                df["Anno"] = anno  # Aggiunge colonna anno
                dati.append(df)
            except Exception as e:
                print(f"Errore nel foglio '{anno}': {e}")

        return pd.concat(dati, ignore_index=True)

    except FileNotFoundError:
        st.error("❌ File 'FsStats.xlsx' non trovato.")
        return pd.DataFrame()


# ===============================

def carica_anno(anno):
    try:
        df = pd.read_excel("FsStats.xlsx", sheet_name=anno)
        df["Anno"] = anno
        return df.drop(columns=["Anno"], errors="ignore")
    except Exception as e:
        print(f"Errore nel caricamento dell'anno '{anno}': {e}")
        return pd.DataFrame()


# ===============================

def stampa_extremes(df, colonna, descrizione, unita=""):
    if df.empty or colonna not in df.columns:
        st.warning("Dati non disponibili per la metrica selezionata.")
        return

    max_row = df.loc[df[colonna].idxmax()]
    min_row = df.loc[df[colonna].idxmin()]

    st.text(f"📈 {max_row['Squadra']} nell'anno {max_row['Anno']} con {max_row[colonna]}{unita} {descrizione}")
    st.text(f"📉 {min_row['Squadra']} nell'anno {min_row['Anno']} con {min_row[colonna]}{unita} {descrizione}")