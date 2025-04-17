import streamlit as st
from utils import carica_dati
from utils import carica_anno
from utils import stampa_extremes
from utils import optionsRecord
from utils import optionsYear

import streamlit as st
import matplotlib.pyplot as plt
from utils import carica_dati

st.title("Dashboard FantaStrambino")
st.subheader("🏆 Classificone")

# Carica i dati da Excel
df = carica_dati()

# Rimuove la colonna 'Pos' se presente
df = df.drop(columns=['Pos'], errors='ignore')

# Calcola presenze (quante volte ogni squadra compare)
presenze = df['Squadra'].value_counts().rename('Pr.')

# Raggruppa per squadra e somma solo le colonne numeriche
classifica = df.groupby('Squadra').sum(numeric_only=True)

# Aggiunge la colonna delle presenze
classifica['Pr.'] = presenze

# Mostra classifica ordinata per punti
st.dataframe(classifica.sort_values(by='Pt.', ascending=False))

##############################################

st.subheader("🥇 Record")

option = st.selectbox(
    'Seleziona anno',
    (optionsYear)
)

st.dataframe(
    carica_anno(option),
    use_container_width=True,
    hide_index=True
)

##############################################

# Prendi solo le label per mostrarle
labels = [label for label, _ in optionsRecord]

# Selezione
selected_label = st.selectbox("Seleziona che dato vuoi vedere negli anni", labels)

# Trova il valore corrispondente
selected_value = dict(optionsRecord)[selected_label]

stampa_extremes(df, selected_value, selected_label)



# Carica tutti i dati
df = carica_dati()

# Raggruppa per squadra e anno, prendi i punti
pivot = df.pivot_table(index='Anno', columns='Squadra', values='Pt.', aggfunc='sum')

# Ordina gli anni (in caso non siano in ordine)
pivot = pivot.reindex(sorted(pivot.index), axis=0)

# Mostra il DataFrame (opzionale)
st.dataframe(pivot)

# Line plot
st.write("📈 Andamento punti per squadra nel tempo")

fig, ax = plt.subplots(figsize=(12, 6))

for squadra in pivot.columns:
    ax.plot(pivot.index, pivot[squadra], marker='o', label=squadra)

ax.set_xlabel("Anno")
ax.set_ylabel("Punti")
ax.set_title("Andamento Punti delle Squadre nel Tempo")
ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')  # Legenda a lato
st.pyplot(fig)