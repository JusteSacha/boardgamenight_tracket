import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from statistics import median
from utils import load_data, save_data, calculate_ticket_moyen, plot_dashboard

st.set_page_config(page_title="BoardGame Profit Tracker", layout="centered")
st.title("🎲 Tableau de bord - Rentabilité Soirées Jeux")

# --- Paramètres ---
SEUIL_RENTABILITE = st.sidebar.number_input("💰 Seuil de rentabilité (€ / personne)", min_value=0.0, value=10.0, step=0.5)

# --- Chargement des données ---
data = load_data()

# --- Formulaire d'ajout ---
st.header("➕ Ajouter une soirée")
with st.form("entry_form"):
    date = st.date_input("📅 Date")
    participants = st.number_input("👥 Nombre de participants", min_value=1, step=1)
    recette = st.number_input("💵 Recette totale (€)", min_value=0.0, step=1.0)
    submitted = st.form_submit_button("Ajouter")
    
    if submitted:
        ticket_moyen = calculate_ticket_moyen(recette, participants)
        new_row = pd.DataFrame([[date, participants, recette, ticket_moyen]], 
                               columns=["Date", "Participants", "Recette", "Ticket Moyen"])
        data = pd.concat([data, new_row], ignore_index=True)
        save_data(data)
        st.success("✅ Soirée ajoutée avec succès !")

# --- Dashboard ---
st.header("📊 Statistiques")
if not data.empty:
    # Conversion et tri
    data["Date"] = pd.to_datetime(data["Date"])
    data = data.sort_values("Date")
    data["Semaine"] = data["Date"].dt.to_period("W").astype(str)

    # Tableau principal
    st.subheader("📅 Détails des soirées")
    st.dataframe(data.style.format({"Recette": "€{:.2f}", "Ticket Moyen": "€{:.2f}"}))

    # 📌 Médiane globale
    mediane_globale = median(data["Ticket Moyen"])
    st.markdown(f"📌 **Médiane globale du ticket moyen :** **€{mediane_globale:.2f}**")

    # 📊 Médiane hebdomadaire
    st.subheader("📈 Médiane du ticket moyen par semaine")
    mediane_par_semaine = data.groupby("Semaine")["Ticket Moyen"].median().reset_index()
    mediane_par_semaine.columns = ["Semaine", "Médiane (€)"]
    st.dataframe(mediane_par_semaine)

    # 📉 Graphiques
    st.subheader("📊 Visualisations")
    plot_dashboard(data, seuil=SEUIL_RENTABILITE)

else:
    st.info("Aucune donnée pour l’instant. Ajoute ta première soirée !")
