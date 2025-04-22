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
# TITOLI E INIZIO
# ===============================
st.title("Dashboard FantaStrambino")
st.subheader("⚽ Classificone")

# Caricamento dati principali
df = carica_dati()
df.columns = df.columns.str.strip()

# ===============================
# 📊 CLASSIFICA GENERALE
# ===============================
df = df.drop(columns=['Pos'], errors='ignore')  # Rimuove colonna Pos se presente
presenze = df['Squadra'].value_counts().rename('Pr.')
classifica = df.groupby('Squadra').sum(numeric_only=True)
classifica['Pr.'] = presenze

st.dataframe(classifica.sort_values(by='Pt.', ascending=False))

# ===============================
# CLASSIFICA PER ANNO
# ===============================
st.subheader("📊 Classifica per anno")
option = st.selectbox("Seleziona anno", optionsYear)
st.dataframe(carica_anno(option), use_container_width=True, hide_index=True)

# ===============================
# 🥇 RECORD STORICI
# ===============================
st.subheader("🥇 Record")
labels = [label for label, _ in optionsRecord]
selected_label = st.selectbox("Seleziona che dato vuoi vedere negli anni", labels)
selected_value = dict(optionsRecord)[selected_label]
stampa_extremes(df, selected_value, selected_label)

# ===============================
# ANDAMENTO PUNTI NEGLI ANNI
# ===============================
st.subheader("🎢 Andamento team")
st.markdown("Per selezionare più squadre dalla legenda, tieni premuto **MAIUSC** (o ⌘ Command su Mac) e clicca sui nomi.")

pivot = df.pivot_table(index='Anno', columns='Squadra', values='Pt.', aggfunc='sum')
pivot = pivot.reindex(sorted(pivot.index))
chart_data = pivot.reset_index().melt(id_vars='Anno', var_name='Squadra', value_name='Punti')
chart_data.dropna(inplace=True)

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
# DISTRIBUZIONE PIAZZAMENTI (BOXPLOT)
# ===============================
st.subheader("📦 Distribuzione Piazzamenti per Squadra")

st.markdown("""
Il boxplot mostra la distribuzione dei piazzamenti in classifica per ogni squadra nelle varie stagioni.

- **Min** e **Max**: miglior e peggior piazzamento ottenuto  
- **Q1 (1º quartile)**: il 25% dei risultati si trova sotto questo valore  
- **Q3 (3º quartile)**: il 75% dei risultati si trova sotto questo valore  
- Insieme Q1 e Q3 formano la "scatola" che contiene la metà centrale dei risultati  
- **Mediana**: il piazzamento tipico (linea dentro la scatola)  
- Un box stretto indica una squadra costante, uno largo indica molta variabilità  
""")

df = carica_dati()
df["Pos"] = pd.to_numeric(df["Pos"], errors="coerce")
df = df.dropna(subset=["Pos"])

boxplot = alt.Chart(df).mark_boxplot(extent='min-max').encode(
    x=alt.X('Squadra:N', sort='y'),
    y=alt.Y('Pos:Q', title="Posizione in Classifica", scale=alt.Scale(reverse=True)),
    color='Squadra:N'
)

mediana_bianca = alt.Chart(df).mark_tick(
    color='white',
    size=20,
    thickness=2
).encode(
    x='Squadra:N',
    y='median(Pos):Q'
)

grafico_finale = (boxplot + mediana_bianca).properties(
    width=800,
    height=400,
    title="📦 Distribuzione Piazzamenti per Squadra"
)

st.altair_chart(grafico_finale, use_container_width=True)

# ===============================
# TROFEI E RETROCESSIONI
# ===============================
st.subheader("🏅 Trofei Totali e Retrocessioni per Team")
st.text("Le retrocessioni sono ufficiali solo a partire dalla stagione 2023-2024.")

albo_df = pd.read_excel("FsStats.xlsx", sheet_name="Albo")
albo_df.columns = albo_df.columns.str.strip()

competizioni = [col for col in albo_df.columns if col.lower() not in ["anno", "retrocessioni"]]

long_albo = pd.melt(
    albo_df,
    id_vars=["Anno"],
    value_vars=competizioni,
    var_name="Competizione",
    value_name="Squadra"
)
long_albo = long_albo[long_albo["Squadra"] != "-"]

conteggio_trofei = (
    long_albo.groupby(["Squadra", "Competizione"])
    .size()
    .unstack(fill_value=0)
    .reset_index()
)
conteggio_trofei["Totale Trofei"] = conteggio_trofei[competizioni].sum(axis=1)

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

conteggio_completo = pd.merge(conteggio_trofei, retro_count, on="Squadra", how="left")
conteggio_completo["Retrocessioni"] = conteggio_completo["Retrocessioni"].fillna(0).astype(int)
conteggio_completo = conteggio_completo.sort_values("Totale Trofei", ascending=False)

st.dataframe(conteggio_completo, hide_index=True)

# ===============================
# MEDIA PUNTI PER POSIZIONE
# ===============================
st.subheader("📈 Media Punti per Posizione")

df["Pt."] = pd.to_numeric(df["Pt."], errors="coerce")
df = df.dropna(subset=["Pt."])

media_punti_per_posizione = (
    df.groupby("Pos")["Pt."]
    .mean()
    .sort_index()
)

for posizione, media in media_punti_per_posizione.items():
    st.markdown(f"- **Posizione {int(posizione)}**: {media:.2f} punti")
