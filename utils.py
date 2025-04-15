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
    fig, ax = plt.subplots(figsize=(8, 4), tight_layout=True)

    ax.plot(data["Date"], data["Ticket Moyen"], marker='o', label="Ticket Moyen")
    ax.axhline(seuil, color='red', linestyle='--', label="Seuil Rentabilité")
    ax.set_title("💸 Ticket Moyen / Soirée")
    ax.set_ylabel("€ / Personne")
    ax.legend()

    st.pyplot(fig)
