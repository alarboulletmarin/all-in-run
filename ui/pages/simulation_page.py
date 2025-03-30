import streamlit as st
from datetime import timedelta

from controllers.simulation_controller import SimulationController
from controllers.plan_controller import PlanController
from utils.date_utils import format_date
from utils.time_converter import format_timedelta, format_pace
from utils.i18n import _ as translate
from ui.components import (
    render_date_selector,
    render_pace_input,
    render_sessions_per_week_selector,
    render_volume_inputs,
    render_comparison_chart
)


def handle_scenario_selection(scenario_index: int):
    """
    Gestionnaire pour la sélection d'un scénario prédéfini

    Args:
        scenario_index: Indice du scénario sélectionné
    """
    if "scenarios" in st.session_state and 0 <= scenario_index < len(st.session_state.scenarios):
        scenario = st.session_state.scenarios[scenario_index]
        st.session_state["simulation_params"] = scenario["params"]


def handle_simulation():
    """
    Gestionnaire pour le lancement d'une simulation
    """
    # Les paramètres de simulation sont déjà dans st.session_state["simulation_params"]
    # On lance simplement la simulation
    st.session_state["run_simulation"] = True


def handle_keep_simulation():
    """
    Gestionnaire pour conserver la simulation comme plan principal
    """
    if "simulated_plan" in st.session_state:
        st.session_state["current_plan"] = st.session_state["simulated_plan"]
        del st.session_state["simulated_plan"]
        st.session_state["page"] = "plan_view"
        st.rerun()


def render_scenario_section(simulation_controller: SimulationController):
    """
    Affiche la section des scénarios prédéfinis

    Args:
        simulation_controller: Contrôleur de simulation
    """
    st.header(translate("predefined_scenarios", "simulation_page"))

    # Vérifier si les scénarios ont déjà été générés
    if "scenarios" not in st.session_state:
        if "user_data" in st.session_state:
            st.session_state["scenarios"] = simulation_controller.get_simulation_scenarios(
                st.session_state["user_data"]
            )
        else:
            st.session_state["scenarios"] = []

    if not st.session_state["scenarios"]:
        st.warning(translate("no_scenarios_available", "simulation_page"))
        return

    # Afficher les scénarios sous forme de cartes
    for i, scenario in enumerate(st.session_state["scenarios"]):
        with st.expander(scenario["name"], expanded=False):
            st.write(scenario["description"])

            # Afficher les paramètres modifiés
            params = scenario["params"]
            st.markdown("**" + translate("modified_parameters", "simulation_page") + ":**")

            for key, value in params.items():
                if key == "start_date" or key == "race_date":
                    st.write(f"- {translate(key, 'simulation_page')}: {format_date(value)}")
                elif "pace" in key and isinstance(value, timedelta):
                    st.write(f"- {translate(key, 'simulation_page')}: {format_pace(value)}")
                else:
                    st.write(f"- {translate(key, 'simulation_page')}: {value}")

            # Bouton pour sélectionner ce scénario
            st.button(
                translate("select_scenario", "simulation_page"),
                key=f"scenario_{i}",
                on_click=handle_scenario_selection,
                args=(i,)
            )


def render_custom_simulation_form():
    """
    Affiche le formulaire de simulation personnalisée
    """
    st.header(translate("custom_simulation", "simulation_page"))

    # Initialiser les paramètres de simulation
    if "simulation_params" not in st.session_state:
        st.session_state["simulation_params"] = {}

    # Vérifier si un plan et des données utilisateur existent
    if "current_plan" not in st.session_state or "user_data" not in st.session_state:
        st.warning(translate("no_plan_available", "simulation_page"))
        return

    user_data = st.session_state["user_data"]

    # Formulaire de simulation
    with st.form(key="simulation_form"):
        st.subheader(translate("training_parameters", "simulation_page"))

        col1, col2 = st.columns(2)

        with col1:
            # Nombre de séances par semaine
            sessions = render_sessions_per_week_selector(
                label=translate("sessions_per_week", "simulation_page"),
                key="sim_sessions_per_week",
                default_value=st.session_state["simulation_params"].get(
                    "sessions_per_week", user_data.sessions_per_week
                )
            )

            # Mettre à jour les paramètres de simulation
            st.session_state["simulation_params"]["sessions_per_week"] = sessions

        with col2:
            # Volumes hebdomadaires
            min_volume, max_volume = render_volume_inputs(
                min_label=translate("min_volume", "simulation_page"),
                max_label=translate("max_volume", "simulation_page"),
                min_key="sim_min_volume",
                max_key="sim_max_volume",
                default_min=st.session_state["simulation_params"].get(
                    "min_volume", user_data.min_volume
                ),
                default_max=st.session_state["simulation_params"].get(
                    "max_volume", user_data.max_volume
                )
            )

            # Mettre à jour les paramètres de simulation
            st.session_state["simulation_params"]["min_volume"] = min_volume
            st.session_state["simulation_params"]["max_volume"] = max_volume

        st.subheader(translate("dates", "simulation_page"))

        col1, col2 = st.columns(2)

        with col1:
            # Date de début
            start_date = render_date_selector(
                label=translate("start_date", "simulation_page"),
                key="sim_start_date",
                default_value=st.session_state["simulation_params"].get(
                    "start_date", user_data.start_date
                ),
                required_weekday=0  # Lundi
            )

            # Mettre à jour les paramètres de simulation
            st.session_state["simulation_params"]["start_date"] = start_date

        with col2:
            # Date de course
            race_date = render_date_selector(
                label=translate("race_date", "simulation_page"),
                key="sim_race_date",
                default_value=st.session_state["simulation_params"].get(
                    "race_date", user_data.main_race.race_date
                ),
                required_weekday=6  # Dimanche
            )

            # Mettre à jour les paramètres de simulation
            st.session_state["simulation_params"]["race_date"] = race_date

        st.subheader(translate("paces", "simulation_page"))

        col1, col2 = st.columns(2)

        with col1:
            # Allure 5K
            pace_5k = render_pace_input(
                label=translate("pace_5k", "simulation_page"),
                key="sim_pace_5k",
                default_value=format_pace(st.session_state["simulation_params"].get(
                    "pace_5k", user_data.pace_5k
                ))
            )

            if pace_5k:
                st.session_state["simulation_params"]["pace_5k"] = pace_5k

            # Allure semi
            pace_half = render_pace_input(
                label=translate("pace_half", "simulation_page"),
                key="sim_pace_half",
                default_value=format_pace(st.session_state["simulation_params"].get(
                    "pace_half_marathon", user_data.pace_half_marathon
                ))
            )

            if pace_half:
                st.session_state["simulation_params"]["pace_half_marathon"] = pace_half

        with col2:
            # Allure 10K
            pace_10k = render_pace_input(
                label=translate("pace_10k", "simulation_page"),
                key="sim_pace_10k",
                default_value=format_pace(st.session_state["simulation_params"].get(
                    "pace_10k", user_data.pace_10k
                ))
            )

            if pace_10k:
                st.session_state["simulation_params"]["pace_10k"] = pace_10k

            # Allure marathon
            pace_marathon = render_pace_input(
                label=translate("pace_marathon", "simulation_page"),
                key="sim_pace_marathon",
                default_value=format_pace(st.session_state["simulation_params"].get(
                    "pace_marathon", user_data.pace_marathon
                ))
            )

            if pace_marathon:
                st.session_state["simulation_params"]["pace_marathon"] = pace_marathon

        # Bouton de simulation
        submit_button = st.form_submit_button(
            translate("run_simulation", "simulation_page"),
            on_click=handle_simulation
        )


def render_comparison_view():
    """
    Affiche la vue de comparaison entre le plan original et le plan simulé
    """
    st.header(translate("comparison", "simulation_page"))

    # Vérifier si un plan simulé existe
    if "simulated_plan" not in st.session_state or "current_plan" not in st.session_state:
        st.warning(translate("no_comparison_available", "simulation_page"))
        return

    original_plan = st.session_state["current_plan"]
    simulated_plan = st.session_state["simulated_plan"]

    # Afficher les différences globales
    col1, col2, col3 = st.columns(3)

    with col1:
        original_volume = original_plan.get_total_volume()
        simulated_volume = simulated_plan.get_total_volume()
        diff_volume = simulated_volume - original_volume
        diff_percent = (diff_volume / original_volume) * 100 if original_volume else 0

        st.metric(
            label=translate("total_volume", "simulation_page"),
            value=f"{simulated_volume} km",
            delta=f"{diff_volume:.1f} km ({diff_percent:.1f}%)"
        )

    with col2:
        original_duration = original_plan.get_total_duration()
        simulated_duration = simulated_plan.get_total_duration()
        diff_duration = simulated_duration - original_duration
        diff_hours = diff_duration.total_seconds() / 3600

        st.metric(
            label=translate("total_duration", "simulation_page"),
            value=format_timedelta(simulated_duration, "hms_text"),
            delta=f"{diff_hours:+.1f}h"
        )

    with col3:
        original_weeks = original_plan.user_data.total_weeks
        simulated_weeks = simulated_plan.user_data.total_weeks
        diff_weeks = simulated_weeks - original_weeks

        st.metric(
            label=translate("total_weeks", "simulation_page"),
            value=simulated_weeks,
            delta=diff_weeks
        )

    # Onglets de comparaison
    tab1, tab2, tab3 = st.tabs([
        translate("volume_comparison", "simulation_page"),
        translate("intensity_comparison", "simulation_page"),
        translate("sessions_comparison", "simulation_page")
    ])

    with tab1:
        render_comparison_chart(original_plan, simulated_plan, "volume")

    with tab2:
        render_comparison_chart(original_plan, simulated_plan, "intensity")

    with tab3:
        render_comparison_chart(original_plan, simulated_plan, "sessions")

    # Bouton pour conserver la simulation comme plan principal
    st.button(
        translate("keep_simulation", "simulation_page"),
        on_click=handle_keep_simulation
    )


def render_simulation_page(
        simulation_controller: SimulationController,
        plan_controller: PlanController
):
    """
    Affiche la page de simulation

    Args:
        simulation_controller: Contrôleur de simulation
        plan_controller: Contrôleur du plan
    """
    st.title(translate("simulation_title", "simulation_page"))

    # Vérifier si un plan existe
    if "current_plan" not in st.session_state and "user_data" not in st.session_state:
        st.warning(translate("no_plan_warning", "simulation_page"))

        # Bouton pour retourner à la page du plan
        if st.button(translate("back_to_plan", "simulation_page")):
            st.session_state["page"] = "plan_view"
            st.rerun()

        return

    # Afficher la section des scénarios prédéfinis
    render_scenario_section(simulation_controller)

    # Afficher le formulaire de simulation personnalisée
    render_custom_simulation_form()

    # Si une simulation doit être lancée
    if st.session_state.get("run_simulation", False):
        with st.spinner(translate("running_simulation", "simulation_page")):
            # Réinitialiser le flag
            st.session_state["run_simulation"] = False

            # Lancer la simulation
            simulated_plan = simulation_controller.simulate_plan(
                st.session_state["user_data"],
                st.session_state["simulation_params"]
            )

            # Stocker le plan simulé
            st.session_state["simulated_plan"] = simulated_plan

            # Afficher un message de succès
            st.success(translate("simulation_success", "simulation_page"))

    # Afficher la comparaison si un plan simulé existe
    if "simulated_plan" in st.session_state:
        render_comparison_view()

    # Bouton pour retourner à la page du plan
    st.divider()

    if st.button(translate("back_to_plan", "simulation_page")):
        st.session_state["page"] = "plan_view"
        st.rerun()