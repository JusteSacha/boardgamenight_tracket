import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from statistics import median
from utils import load_data, save_data, calculate_ticket_moyen, plot_dashboard

# --- Configuration de la page ---
st.set_page_config(page_title="BoardGame Profit Tracker", layout="centered")
st.title("🎲 Tracker des soirées jeux")

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

# --- Fonction de projection ---
def afficher_projection_ticket_moyen(data):
    st.subheader("🔮 Projection du ticket moyen et de la fréquentation (3 mois)")

    df = data.copy().sort_values("Date")
    df["Date"] = pd.to_datetime(df["Date"])
    df["Date_ordinal"] = df["Date"].apply(lambda x: x.toordinal())

    X = df[["Date_ordinal"]]
    y_ticket_moyen = df["Ticket Moyen"]
    y_participants = df["Participants"]

    model_ticket = LinearRegression().fit(X, y_ticket_moyen)
    model_participants = LinearRegression().fit(X, y_participants)

    future_dates = pd.date_range(df["Date"].max(), periods=90)
    future_ordinals = np.array([d.toordinal() for d in future_dates]).reshape(-1, 1)

    future_ticket = model_ticket.predict(future_ordinals)
    future_freq = model_participants.predict(future_ordinals)

    fig, ax1 = plt.subplots(figsize=(10, 4))

    ax1.plot(df["Date"], y_ticket_moyen, marker="o", color='blue', label="Historique Ticket Moyen")
    ax1.plot(future_dates, future_ticket, linestyle="--", color="orange", label="Projection Ticket Moyen")
    ax1.set_ylabel("€ / personne", color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')

    ax2 = ax1.twinx()
    ax2.plot(df["Date"], y_participants, marker="o", color='green', label="Historique Fréquentation")
    ax2.plot(future_dates, future_freq, linestyle="--", color="purple", label="Projection Fréquentation")
    ax2.set_ylabel("Participants", color='green')
    ax2.tick_params(axis='y', labelcolor='green')

    ax1.set_title("Projection du ticket moyen et de la fréquentation (3 mois)")
    ax1.legend(loc="upper left")
    ax2.legend(loc="upper right")

    st.pyplot(fig)

# --- Dashboard principal ---
st.header("📊 Statistiques")

if not data.empty:
    data["Date"] = pd.to_datetime(data["Date"])
    data = data.sort_values("Date")

    st.subheader("📅 Détails des soirées")
    st.dataframe(data.style.format({"Recette": "€{:.2f}", "Ticket Moyen": "€{:.2f}"}))

    # Médiane globale du ticket moyen
    mediane_globale = median(data["Ticket Moyen"])
    st.markdown(f"📌 **Médiane globale du ticket moyen :** **€{mediane_globale:.2f}**")

    # Visualisation de la rentabilité
    st.subheader("📈 Visualisations")
    plot_dashboard(data, seuil=SEUIL_RENTABILITE)

    # Graphe fréquentation vs recette
    fig, ax1 = plt.subplots(figsize=(10, 6))

    ax1.plot(data["Date"], data["Recette"], marker="o", color="blue", linestyle="--", label="Recette Totale (€)")
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Recette (€)", color="blue")
    ax1.tick_params(axis='y', labelcolor="blue")

    ax2 = ax1.twinx()
    ax2.bar(data["Date"], data["Participants"], color="green", alpha=0.6, label="Fréquentation (Participants)")
    ax2.set_ylabel("Fréquentation (Participants)", color="green")
    ax2.tick_params(axis='y', labelcolor="green")
    ax2.set_ylim(0, data["Participants"].max() * 1.2)

    ax1.set_title("Relation entre Recette Totale et Fréquentation")
    ax1.legend(loc="upper left")
    ax2.legend(loc="upper right")

    st.pyplot(fig)

    # Projections
    afficher_projection_ticket_moyen(data)

else:
    st.info("Aucune donnée pour l’instant. Ajoute ta première soirée !")
