import streamlit as st
from utils import carica_dati
from utils import carica_anno
from utils import stampa_extremes
from utils import optionsRecord
from utils import optionsYear

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


