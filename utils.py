# utils.py
import pandas as pd
import streamlit as st

optionsRecord = [
    ("Vittorie", "V"),
    ("Pareggi", "N"),
    ("Sconfitte", "P"),
    ("Gol fatti", "Gf"),
    ("Gol subiti", "Gs"),
    ("Punti", "Pt."),
    ("Punti Totali", "Pt. Totali")
]

optionsYear = [
    '16-17', '17-18', '18-19', '19-20', '20-21', '21-22', '22-23', '23-24'
]

def carica_dati():
    file_excel = pd.ExcelFile("FsStats.xlsx")
    fogli = file_excel.sheet_names
    dati = []

    for anno in fogli:
        try:
            df = file_excel.parse(anno)
            df["Anno"] = anno
            dati.append(df)
        except Exception as e:
            print(f"Errore nel foglio {anno}: {e}")
    
    return pd.concat(dati, ignore_index=True)

def carica_anno(anno):
    file_excel = pd.ExcelFile("FsStats.xlsx")

    try:
        df = file_excel.parse(anno)
        df["Anno"] = anno

        df = df.drop(columns=['Anno'], errors='ignore')     
        return df

    except Exception as e:
        print(f"Errore nel foglio '{anno}': {e}")
        return pd.DataFrame()
    
def stampa_extremes(df, colonna, descrizione, unita=""):

    # Estremi
    max_row = df.loc[df[colonna].idxmax()]
    min_row = df.loc[df[colonna].idxmin()]

    st.text(f"🔺 {max_row['Squadra']} nell'anno {max_row['Anno']} con {max_row[colonna]}{unita} {descrizione}")
    st.text(f"🔻 {min_row['Squadra']} nell'anno {min_row['Anno']} con {min_row[colonna]}{unita} {descrizione}")

     