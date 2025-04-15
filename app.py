import numpy as np
from sklearn.linear_model import LinearRegression
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

# --- Définition de la fonction de projection ---
def afficher_projection_ticket_moyen(data):
    st.subheader("🔮 Projection du ticket moyen et de la fréquentation (3 mois)")

    # Préparer les données
    df = data.copy()
    df = df.sort_values("Date")
    df["Date_ordinal"] = df["Date"].apply(lambda x: x.toordinal())
    
    X = df[["Date_ordinal"]]
    y_ticket_moyen = df["Ticket Moyen"]
    y_participants = df["Participants"]

    # Modèles de régression pour ticket moyen et fréquentation
    model_ticket_moyen = LinearRegression()
    model_ticket_moyen.fit(X, y_ticket_moyen)

    model_participants = LinearRegression()
    model_participants.fit(X, y_participants)

    # Générer les dates futures (90 jours)
    future_dates = pd.date_range(df["Date"].max(), periods=90)
    future_ordinals = np.array([d.toordinal() for d in future_dates]).reshape(-1, 1)

    # Prédictions pour ticket moyen et fréquentation
    future_preds_ticket_moyen = model_ticket_moyen.predict(future_ordinals)
    future_preds_participants = model_participants.predict(future_ordinals)

    # Affichage
    fig, ax1 = plt.subplots(figsize=(10, 4))

    # Affichage de la projection du ticket moyen
    ax1.plot(df["Date"], y_ticket_moyen, marker="o", label="Historique Ticket Moyen", color='b')
    ax1.plot(future_dates, future_preds_ticket_moyen, color="orange", linestyle="--", label="Projection Ticket Moyen (90 jours)")
    ax1.set_ylabel("€ / personne", color='b')
    ax1.tick_params(axis='y', labelcolor='b')

    # Création d'un axe secondaire pour la fréquentation
    ax2 = ax1.twinx()  
    ax2.plot(df["Date"], y_participants, marker="o", label="Historique Fréquentation", color='g')
    ax2.plot(future_dates, future_preds_participants, color="purple", linestyle="--", label="Projection Fréquentation (90 jours)")
    ax2.set_ylabel("Participants", color='g')
    ax2.tick_params(axis='y', labelcolor='g')

    # Titre et légende
    ax1.set_title("Projection du ticket moyen et de la fréquentation à 3 mois")
    ax1.legend(loc="upper left")
    ax2.legend(loc="upper right")

    # Affichage du graphique
    st.pyplot(fig)

# --- Dashboard ---
st.header("📊 Statistiques")
if not data.empty:
    # Conversion Date
    data["Date"] = pd.to_datetime(data["Date"])
    data = data.sort_values("Date")

    st.subheader("📅 Détails des soirées")
    st.dataframe(data.style.format({"Recette": "€{:.2f}", "Ticket Moyen": "€{:.2f}"}))

    # 📌 Médiane globale
    mediane_globale = median(data["Ticket Moyen"])
    st.markdown(f"📌 **Médiane globale du ticket moyen :** **€{mediane_globale:.2f}**")

    # 📈 Graphiques
    st.subheader("📈 Visualisations")

def plot_dashboard(data, seuil):
    # Initialisation du graphique
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Tracer les recettes en fonction de la date
    ax1.plot(data["Date"], data["Recette"], marker="o", label="Recette Totale (€)", color="blue", linestyle="--")
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Recette (€)", color="blue")
    ax1.tick_params(axis='y', labelcolor="blue")

    # Créer un axe secondaire pour la fréquentation
    ax2 = ax1.twinx()  
    ax2.bar(data["Date"], data["Participants"], color="green", alpha=0.6, label="Fréquentation (Participants)")

    # Ajuster l'échelle pour l'axe secondaire
    max_participants = max(data["Participants"])
    ax2.set_ylabel("Fréquentation (Participants)", color="green")
    ax2.tick_params(axis='y', labelcolor="green")

    # Titre et légende
    ax1.set_title("Relation entre Recette Totale et Fréquentation des Soirées")
    ax2.set_ylim(0, max_participants * 1.2)  # Ajuster l'échelle pour les barres
    ax2.legend(loc="upper right")
    ax1.legend(loc="upper left")

    # Affichage du graphique
    st.pyplot(fig)


    afficher_projection_ticket_moyen(data)  # Cette fonction gère également la projection du ticket moyen et de la fréquentation

else:
    st.info("Aucune donnée pour l’instant. Ajoute ta première soirée !")
