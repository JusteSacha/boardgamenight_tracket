import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

DATA_FILE = "data.csv"

def load_data():
    try:
        return pd.read_csv(DATA_FILE)
    except FileNotFoundError:
        return pd.DataFrame(columns=["Date", "Participants", "Recette", "Ticket Moyen"])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

def calculate_ticket_moyen(recette, participants):
    return round(recette / participants, 2)

def plot_dashboard(data, seuil):
    fig, ax = plt.subplots(2, 1, figsize=(8, 6), tight_layout=True)

    ax[0].plot(data["Date"], data["Ticket Moyen"], marker='o', label="Ticket Moyen")
    ax[0].axhline(seuil, color='red', linestyle='--', label="Seuil Rentabilité")
    ax[0].set_title("💸 Ticket Moyen / Soirée")
    ax[0].set_ylabel("€ / Personne")
    ax[0].legend()

    ax[1].bar(data["Date"], data["Participants"], alpha=0.6, label="Participants")
    ax[1].plot(data["Date"], data["Recette"], color="green", label="Recette (€)", linewidth=2)
    ax[1].set_title("📈 Fréquentation & Recette")
    ax[1].set_ylabel("Nbre / €")
    ax[1].legend()

    st.pyplot(fig)