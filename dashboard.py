import streamlit as st
import pandas as pd
import altair as alt

from utils import (
    carica_dati,
    carica_anno,
    stampa_extremes,
    optionsRecord,
    optionsYear
)

# ===============================

st.title("Dashboard FantaStrambino")
st.subheader("⚽ Classificone")

# ===============================

df = carica_dati()

# Rimuove colonna "Pos" se esiste
df = df.drop(columns=['Pos'], errors='ignore')

# Calcola presenze (quante stagioni ha partecipato ogni squadra)
presenze = df['Squadra'].value_counts().rename('Pr.')

# Raggruppa per squadra e somma i valori numerici
classifica = df.groupby('Squadra').sum(numeric_only=True)
classifica['Pr.'] = presenze

# Mostra la classifica ordinata per punti
st.dataframe(classifica.sort_values(by='Pt.', ascending=False))

# ===============================

st.subheader("🥇 Record")

# Selettore per anno
option = st.selectbox("Seleziona anno", optionsYear)

# Mostra i dati dell’anno selezionato
st.dataframe(carica_anno(option), use_container_width=True, hide_index=True)

# ===============================

# Selettore tipo di record
labels = [label for label, _ in optionsRecord]
selected_label = st.selectbox("Seleziona che dato vuoi vedere negli anni", labels)
selected_value = dict(optionsRecord)[selected_label]

# Mostra i record estremi per il tipo selezionato
stampa_extremes(df, selected_value, selected_label)

# ===============================

st.subheader("📊 Andamento team")

# Crea pivot: anni in riga, squadre in colonna, valori = punti
pivot = df.pivot_table(index='Anno', columns='Squadra', values='Pt.', aggfunc='sum')
pivot = pivot.reindex(sorted(pivot.index))  # Ordina per anno

# Trasforma in formato long per grafico
chart_data = pivot.reset_index().melt(id_vars='Anno', var_name='Squadra', value_name='Punti')
chart_data.dropna(inplace=True)

# Grafico Altair con selezione multipla
highlight = alt.selection_multi(fields=["Squadra"], bind="legend")

chart = (
    alt.Chart(chart_data)
    .mark_line(point=True)
    .encode(
        x="Anno:O",
        y="Punti:Q",
        color="Squadra:N",
        opacity=alt.condition(highlight, alt.value(1), alt.value(0.15)),
        tooltip=["Anno", "Squadra", "Punti"]
    )
    .add_selection(highlight)
    .properties(width=800, height=400)
)

st.altair_chart(chart, use_container_width=True)

# ===============================

st.subheader("🏅 Trofei Totali e Retrocessioni per Team")
st.text("Le retrocessioni sono ufficiali solo a partire dalla stagione 2023-2024.")

# Carica il foglio "Albo" da Excel
albo_df = pd.read_excel("FsStats.xlsx", sheet_name="Albo")
albo_df.columns = albo_df.columns.str.strip()

# Identifica le competizioni escludendo anno e retrocessioni
competizioni = [col for col in albo_df.columns if col.lower() not in ["anno", "retrocessioni"]]

# 📊 Trasforma in formato lungo per conteggio trofei
long_albo = pd.melt(
    albo_df,
    id_vars=["Anno"],
    value_vars=competizioni,
    var_name="Competizione",
    value_name="Squadra"
)
long_albo = long_albo[long_albo["Squadra"] != "-"]  # Elimina righe con '-'

# Conta trofei per squadra e competizione
conteggio_trofei = (
    long_albo.groupby(["Squadra", "Competizione"])
    .size()
    .unstack(fill_value=0)
    .reset_index()
)
conteggio_trofei["Totale Trofei"] = conteggio_trofei[competizioni].sum(axis=1)

# 📉 Conta retrocessioni
retro_data = albo_df[["Anno", "Retrocessioni"]].dropna()
retro_expanded = (
    retro_data["Retrocessioni"]
    .str.split(",", expand=True)
    .stack()
    .str.strip()
    .reset_index(drop=True)
    .to_frame(name="Squadra")
)
retro_count = retro_expanded["Squadra"].value_counts().reset_index()
retro_count.columns = ["Squadra", "Retrocessioni"]

# 🔗 Unisce trofei e retrocessioni
conteggio_completo = pd.merge(conteggio_trofei, retro_count, on="Squadra", how="left")
conteggio_completo["Retrocessioni"] = conteggio_completo["Retrocessioni"].fillna(0).astype(int)

# Ordina per trofei
conteggio_completo = conteggio_completo.sort_values("Totale Trofei", ascending=False)

# Mostra il risultato finale
st.dataframe(conteggio_completo, hide_index=True)