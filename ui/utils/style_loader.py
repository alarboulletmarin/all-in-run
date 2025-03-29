import os
import streamlit as st


def load_css(file_name):
    """
    Charge et applique un fichier CSS à l'application Streamlit

    Args:
        file_name (str): Nom du fichier CSS à charger
    """
    css_folder = os.path.join(os.path.dirname(
        os.path.dirname(__file__)), "static", "css")
    with open(os.path.join(css_folder, file_name)) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def load_all_css():
    """Charge tous les fichiers CSS principaux de l'application"""
    load_css("main.css")


def load_calendar_css():
    """Charge les styles spécifiques au calendrier"""
    load_css("calendar.css")
