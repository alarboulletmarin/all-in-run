"""
Application All-in-Run améliorée avec une interface responsive et une meilleure expérience utilisateur.
Point d'entrée principal de l'application.
"""
from controllers.simulation_controller import SimulationController
from controllers.plan_controller import PlanController
from controllers.input_controller import InputController
from ui.pages.simulation_page import render_simulation_page
from ui.pages.plan_view_page import render_plan_view_page
from ui.pages.input_page import render_input_form
from config.languages import DEFAULT_LANGUAGE
from utils.i18n import i18n, _
import streamlit as st
import os
import sys

# Ajout du chemin racine au PYTHONPATH pour permettre des imports relatifs
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Maintenant utiliser des imports absolus plutôt que relatifs

# Importation des pages de l'interface (nouvelles versions améliorées)

# Importation des contrôleurs


def render_language_selector():
    """Affiche un sélecteur de langue dans la barre latérale"""
    from config.languages import AVAILABLE_LANGUAGES

    current_lang = i18n.get_current_language()

    # Créer une liste de noms de langues pour l'affichage
    lang_names = [name for _, name in AVAILABLE_LANGUAGES]
    lang_codes = [code for code, _ in AVAILABLE_LANGUAGES]

    # Trouver l'index de la langue courante
    current_index = lang_codes.index(
        current_lang) if current_lang in lang_codes else 0

    # Afficher le sélecteur de langue
    selected_lang_name = st.sidebar.selectbox(
        "🌍 Langue / Language",
        lang_names,
        index=current_index
    )

    # Trouver le code correspondant au nom sélectionné
    selected_index = lang_names.index(selected_lang_name)
    selected_lang_code = lang_codes[selected_index]

    # Changer la langue si nécessaire
    if selected_lang_code != current_lang:
        i18n.switch_language(selected_lang_code)
        st.rerun()  # Recharger l'interface pour appliquer la nouvelle langue


def initialize_session_state():
    """Initialise l'état de session Streamlit"""
    # Définir la langue par défaut
    if "language" not in st.session_state:
        st.session_state["language"] = DEFAULT_LANGUAGE

    # Définir la page par défaut
    if "page" not in st.session_state:
        st.session_state["page"] = "input"

    # Initialiser les contrôleurs si nécessaire
    if "input_controller" not in st.session_state:
        st.session_state["input_controller"] = InputController()

    if "plan_controller" not in st.session_state:
        st.session_state["plan_controller"] = PlanController()

    if "simulation_controller" not in st.session_state:
        st.session_state["simulation_controller"] = SimulationController()


def get_controllers():
    """Récupère les contrôleurs depuis l'état de session"""
    input_controller = st.session_state["input_controller"]
    plan_controller = st.session_state["plan_controller"]
    simulation_controller = st.session_state["simulation_controller"]

    return input_controller, plan_controller, simulation_controller


def setup_page_config():
    """Configure les paramètres de la page et le CSS personnalisé"""
    # Configuration de base de la page
    st.set_page_config(
        page_title="All-in-Run",
        page_icon="🏃",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Charger les styles CSS
    from ui.utils.style_loader import load_all_css
    load_all_css()


def render_sidebar():
    """Affiche le contenu de la barre latérale"""
    # Logo et titre
    st.sidebar.title("All in Run 🏃")

    # Sélection de langue
    render_language_selector()

    # Navigation principale
    st.sidebar.header(_("navigation", "common") or "Navigation")

    # Déterminer la page active
    current_page = st.session_state.get("page", "input")

    # Vérifier si un plan a été généré
    plan_exists = st.session_state.get("plan_generated", False)

    # Afficher les boutons de navigation
    if st.sidebar.button(
            _("create_plan", "common") or "Créer un plan",
            use_container_width=True,
            type="primary" if current_page == "input" else "secondary"
    ):
        st.session_state["page"] = "input"
        st.rerun()

    if st.sidebar.button(
            _("view_plan", "common") or "Voir mon plan",
            use_container_width=True,
            disabled=not plan_exists,
            type="primary" if current_page == "plan_view" else "secondary"
    ):
        st.session_state["page"] = "plan_view"
        st.rerun()

    if st.sidebar.button(
            _("simulate", "common") or "Simuler des variantes",
            use_container_width=True,
            disabled=not plan_exists,
            type="primary" if current_page == "simulation" else "secondary"
    ):
        st.session_state["page"] = "simulation"
        st.rerun()

    # Informations supplémentaires
    st.sidebar.divider()
    st.sidebar.info(_(
        "app_description",
        "common"
    ) or """
    All-in-Run vous aide à générer un plan d'entraînement personnalisé pour vos courses de fond.
    """)

    # Pied de page
    st.sidebar.divider()
    st.sidebar.caption("© 2025 All-in-Run")


def main():
    """Fonction principale de l'application"""
    setup_page_config()

    # Initialiser l'état de session
    initialize_session_state()

    # Afficher la barre latérale
    render_sidebar()

    # Récupérer les contrôleurs
    input_controller, plan_controller, simulation_controller = get_controllers()

    # Afficher la page demandée
    current_page = st.session_state["page"]

    if current_page == "input":
        # Appel à la page d'entrée
        render_input_form(input_controller)

    elif current_page == "plan_view":
        # Appel à la page d'affichage du plan
        render_plan_view_page(plan_controller)

    elif current_page == "simulation":
        # Appel à la page de simulation
        render_simulation_page(simulation_controller, plan_controller)

    else:
        st.error(_("page_not_found", "common"))


if __name__ == "__main__":
    main()
