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

# Configuration du chemin d'accès pour permettre l'import des modules
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)


def render_language_selector():
    """Affiche un sélecteur de langue dans la barre latérale et applique la langue choisie"""
    from config.languages import AVAILABLE_LANGUAGES

    current_lang = i18n.get_current_language()

    # Liste des noms et codes de langues disponibles
    lang_names = [name for _, name in AVAILABLE_LANGUAGES]
    lang_codes = [code for code, _ in AVAILABLE_LANGUAGES]

    # Positionnement sur la langue actuelle
    current_index = lang_codes.index(
        current_lang) if current_lang in lang_codes else 0

    # Interface du sélecteur de langue
    selected_lang_name = st.sidebar.selectbox(
        "🌍 Langue / Language",
        lang_names,
        index=current_index
    )

    # Mise à jour de la langue si changement détecté
    selected_index = lang_names.index(selected_lang_name)
    selected_lang_code = lang_codes[selected_index]

    if selected_lang_code != current_lang:
        i18n.switch_language(selected_lang_code)
        st.rerun()  # Rechargement de l'interface pour appliquer la nouvelle langue


def initialize_session_state():
    """Initialise les variables d'état de session Streamlit nécessaires au fonctionnement de l'application"""
    # Configuration de la langue par défaut
    if "language" not in st.session_state:
        st.session_state["language"] = DEFAULT_LANGUAGE

    # Configuration de la page d'accueil par défaut
    if "page" not in st.session_state:
        st.session_state["page"] = "input"

    # Instanciation des contrôleurs principaux
    if "input_controller" not in st.session_state:
        st.session_state["input_controller"] = InputController()

    if "plan_controller" not in st.session_state:
        st.session_state["plan_controller"] = PlanController()

    if "simulation_controller" not in st.session_state:
        st.session_state["simulation_controller"] = SimulationController()


def get_controllers():
    """Récupère les instances des contrôleurs depuis l'état de session"""
    input_controller = st.session_state["input_controller"]
    plan_controller = st.session_state["plan_controller"]
    simulation_controller = st.session_state["simulation_controller"]

    return input_controller, plan_controller, simulation_controller


def setup_page_config():
    """Configure l'apparence et les paramètres généraux de l'application"""
    # Configuration générale de la page
    st.set_page_config(
        page_title="All-in-Run",
        page_icon="🏃",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Chargement des styles CSS personnalisés
    from ui.utils.style_loader import load_all_css
    load_all_css()


def render_sidebar():
    """Construit la barre latérale avec la navigation et les informations de l'application"""
    # En-tête avec logo
    st.sidebar.title("All in Run 🏃")

    # Ajout du sélecteur de langue
    render_language_selector()

    # Menu de navigation
    st.sidebar.header(_("navigation", "common") or "Navigation")

    current_page = st.session_state.get("page", "input")
    plan_exists = st.session_state.get("plan_generated", False)

    # Boutons de navigation avec état actif/inactif selon le contexte
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

    # Section d'information sur l'application
    st.sidebar.divider()
    st.sidebar.info(_(
        "app_description",
        "common"
    ) or """
    All-in-Run vous aide à générer un plan d'entraînement personnalisé pour vos courses de fond.
    """)

    # Pied de page avec copyright
    st.sidebar.divider()
    st.sidebar.caption("© 2025 All-in-Run")


def main():
    """Point d'entrée principal de l'application - orchestration du flux d'exécution"""
    setup_page_config()

    # Initialisation de l'état
    initialize_session_state()

    # Affichage de l'interface utilisateur
    render_sidebar()

    # Récupération des contrôleurs nécessaires
    input_controller, plan_controller, simulation_controller = get_controllers()

    # Routage vers la page appropriée selon l'état actuel
    current_page = st.session_state["page"]

    if current_page == "input":
        render_input_form(input_controller)
    elif current_page == "plan_view":
        render_plan_view_page(plan_controller)
    elif current_page == "simulation":
        render_simulation_page(simulation_controller, plan_controller)
    else:
        st.error(_("page_not_found", "common"))


if __name__ == "__main__":
    main()
