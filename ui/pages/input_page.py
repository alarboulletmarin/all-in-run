"""
Page de saisie des données utilisateur.
"""
import streamlit as st
from datetime import date, timedelta

from controllers.input_controller import InputController
from models.course import RaceType
from ui.components.forms import render_date_with_weekday_constraint
from utils.date_utils import get_next_monday, get_sunday, format_date
from utils.time_converter import format_pace
from utils.i18n import _ as translate
from config.constants import (
    MIN_WEEKS_BEFORE_RACE,
    DEFAULT_MIN_VOLUME,
    DEFAULT_MAX_VOLUME,
    DEFAULT_SESSIONS_PER_WEEK
)
from ui.components.responsive_layout import responsive_columns, card
from ui.components import (
    render_date_selector,
    render_pace_input,
    render_time_input,
    render_race_type_selector,
    render_sessions_per_week_selector,
    render_volume_inputs
)


def render_input_form(input_controller: InputController):
    """
    Affiche le formulaire de saisie des données utilisateur avec une interface améliorée

    Args:
        input_controller: Contrôleur de saisie
    """
    st.title(translate("create_plan_title", "input_page"))

    # Charger les entrées précédentes si disponibles
    saved_input = input_controller.load_input()

    # Initialiser les courses intermédiaires
    if "intermediate_races" not in st.session_state:
        st.session_state.intermediate_races = saved_input.get("intermediate_races", [])

    # Utiliser une mise en page en onglets pour organiser le contenu
    tab_main, tab_paces, tab_intermediate = st.tabs([
        translate("main_info", "input_page"),
        translate("paces_settings", "input_page"),
        translate("intermediate_races", "input_page")
    ])

    # Onglet 1: Informations principales
    with tab_main:
        with st.form(key="main_form"):
            st.subheader(translate("race_info", "input_page"))

            # Utiliser des colonnes responsives pour les informations de base
            col1, col2 = responsive_columns([1, 1])

            with col1:
                race_type = render_race_type_selector(
                    label=translate("race_type", "input_page"),
                    key="race_type",
                    default_value=saved_input.get("race_type", RaceType.TEN_K.value)
                )

                # Champs spécifiques pour le type "autre"
                distance = None
                target_time = None

                if race_type == RaceType.OTHER.value:
                    distance = st.number_input(
                        label=translate("race_distance", "input_page"),
                        min_value=1.0,
                        max_value=100.0,
                        value=saved_input.get("distance", 10.0),
                        step=0.1,
                        key="distance",
                        help=translate("race_distance_help", "input_page")
                    )

                    target_time = render_time_input(
                        label=translate("race_target_time", "input_page"),
                        key="target_time",
                        default_hours=saved_input.get("target_time_hours", 0),
                        default_minutes=saved_input.get("target_time_minutes", 45),
                        default_seconds=saved_input.get("target_time_seconds", 0),
                        help=translate("target_time_help", "input_page")
                    )

            with col2:
                # Dates de début et de course
                today = date.today()

                # Ajouter une information visuelle sur la date minimale de course
                min_date_info = st.empty()

                start_date = render_date_with_weekday_constraint(
                    label=translate("start_date", "input_page"),
                    key="start_date",
                    required_weekday=0,  # Lundi
                    default_value=saved_input.get("start_date", get_next_monday(today)),
                    min_value=today,
                    help_text=translate("start_date_help", "input_page")
                )

                min_race_date = start_date + timedelta(days=MIN_WEEKS_BEFORE_RACE * 7)

                st.info(f"Date minimale pour la course : {format_date(get_sunday(min_race_date))}")

                race_date = render_date_with_weekday_constraint(
                    label=translate("race_date", "input_page"),
                    required_weekday=6,  # Dimanche
                    key="race_date",
                    default_value=saved_input.get("race_date", get_sunday(min_race_date)),
                    min_value=min_race_date,
                    help_text=translate("race_date_help", "input_page")
                )

                # Vérifier l'écart entre les dates et afficher une information visuelle
                days_diff = (race_date - start_date).days
                weeks_diff = (race_date - start_date).days // 7

            st.subheader(translate("training_params", "input_page"))

            col1, col2 = responsive_columns([1, 1])

            with col1:
                sessions = render_sessions_per_week_selector(
                    label=translate("sessions_per_week", "input_page"),
                    key="sessions_per_week",
                    default_value=saved_input.get("sessions_per_week", DEFAULT_SESSIONS_PER_WEEK),
                    help_text=translate("sessions_per_week_help", "input_page")
                )

            with col2:
                min_volume, max_volume = render_volume_inputs(
                    min_label=translate("min_volume", "input_page"),
                    max_label=translate("max_volume", "input_page"),
                    min_key="min_volume",
                    max_key="max_volume",
                    default_min=saved_input.get("min_volume", DEFAULT_MIN_VOLUME),
                    default_max=saved_input.get("max_volume", DEFAULT_MAX_VOLUME),
                    help_text=translate("volume_help", "input_page")
                )

            # Bouton de soumission principal en bas du formulaire
            st.markdown("### " + translate("create_plan", "input_page"))
            submit_button = st.form_submit_button(
                translate("generate_plan", "input_page"),
                use_container_width=True,
                type="primary"
            )

    # Onglet 2: Allures
    with tab_paces:
        with st.form(key="paces_form"):
            st.subheader(translate("user_paces", "input_page"))

            # Afficher un cadre explicatif sur les allures
            st.info(translate("paces_explanation", "input_page") or "Les allures doivent respecter l'ordre: 5K < 10K < Semi < Marathon (plus la distance est longue, plus l'allure est lente).")

            # Organiser les allures en deux colonnes
            col1, col2 = responsive_columns([1, 1])

            with col1:
                pace_5k = render_pace_input(
                    label=translate("pace_5k", "input_page"),
                    key="pace_5k",
                    default_value=saved_input.get("pace_5k_str", "04:30")
                )

                pace_half = render_pace_input(
                    label=translate("pace_half", "input_page"),
                    key="pace_half",
                    default_value=saved_input.get("pace_half_str", "05:00")
                )

            with col2:
                pace_10k = render_pace_input(
                    label=translate("pace_10k", "input_page"),
                    key="pace_10k",
                    default_value=saved_input.get("pace_10k_str", "04:45")
                )

                pace_marathon = render_pace_input(
                    label=translate("pace_marathon", "input_page"),
                    key="pace_marathon",
                    default_value=saved_input.get("pace_marathon_str", "05:30")
                )

            # Vérifier l'ordre des allures
            if all([pace_5k, pace_10k, pace_half, pace_marathon]):
                if not (pace_5k < pace_10k < pace_half < pace_marathon):
                    st.warning(translate("pace_order_warning", "input_page"))
                else:
                    st.success(translate("paces_valid", "input_page") or "Vos allures sont cohérentes.")

            # Bouton secondaire pour sauvegarder uniquement les allures
            save_paces = st.form_submit_button(
                translate("save_paces", "input_page") or "Enregistrer mes allures",
                use_container_width=True
            )

    # Onglet 3: Courses intermédiaires
    with tab_intermediate:
        st.subheader(translate("intermediate_races", "input_page"))

        # Section interactive avec les courses existantes
        if st.session_state.intermediate_races:
            st.write(translate("existing_races", "input_page") or "Courses intermédiaires configurées:")

            # Afficher les courses intermédiaires existantes dans une grille
            for i, race in enumerate(st.session_state.intermediate_races):
                # Utiliser des cartes pour chaque course
                card(
                    title=f"{translate('intermediate_race', 'forms')} {i + 1}: {race.get('race_date', date.today())}",
                    content=f"""
                    **Type**: {race.get('race_type', RaceType.TEN_K.value)}  
                    **Date**: {race.get('race_date', date.today())}  
                    **Allure visée**: {race.get('target_pace_str', '00:00')}
                    """,
                    footer=f"""
                    <button kind="secondary" 
                    onclick="document.getElementById('delete_race_{i}').click()">
                    {translate('delete_race', 'forms')}
                    </button>
                    """,
                    is_expanded=True
                )

                # Bouton caché pour la suppression
                if st.button(f"delete_race_{i}", key=f"delete_race_{i}", disabled=False):
                    st.session_state.intermediate_races.pop(i)
                    st.rerun()
        else:
            st.info(translate("no_intermediate_races", "input_page") or "Aucune course intermédiaire n'a été ajoutée.")

        # Interface d'ajout de course
        with st.expander(translate("add_new_race", "input_page") or "Ajouter une nouvelle course intermédiaire", expanded=not st.session_state.intermediate_races):
            # Déterminer la date par défaut pour la nouvelle course
            if st.session_state.get("start_date") and st.session_state.get("race_date"):
                # Placer par défaut à mi-chemin entre début et course principale
                start = st.session_state["start_date"]
                end = st.session_state["race_date"]
                mid_point = start + (end - start) // 2
                # Ajuster au dimanche
                default_date = get_sunday(mid_point)
            else:
                # Si pas de dates définies, prendre un dimanche dans 30 jours
                default_date = get_sunday(date.today() + timedelta(days=30))

            col1, col2 = responsive_columns([1, 1])

            with col1:
                new_race_date = render_date_selector(
                    label=translate("race_date", "forms"),
                    key="new_intermediate_race_date",
                    default_value=default_date,
                    required_weekday=6,  # Dimanche
                    help_text=translate("intermediate_race_date_help", "forms")
                )

                new_race_type = render_race_type_selector(
                    label=translate("race_type", "forms"),
                    key="new_intermediate_race_type",
                    default_value=RaceType.TEN_K.value
                )

            with col2:
                # Distance pour les courses de type "autre"
                new_race_distance = None
                if new_race_type == RaceType.OTHER.value:
                    new_race_distance = st.number_input(
                        label=translate("race_distance", "forms"),
                        min_value=1.0,
                        max_value=100.0,
                        value=10.0,
                        step=0.1,
                        key="new_intermediate_race_distance"
                    )

                # Allure visée
                new_race_pace = render_pace_input(
                    label=translate("target_pace", "forms"),
                    key="new_intermediate_race_pace",
                    default_value="05:30"
                )

            # Objectif de la course
            new_race_objective = st.selectbox(
                label=translate("race_objective", "forms"),
                options=["Compétition", "Entraînement", "Test"],
                index=0,
                key="new_intermediate_race_objective"
            )

            # Bouton pour ajouter la course
            if st.button(translate("add_intermediate_race", "input_page"), use_container_width=True):
                # Créer la nouvelle course
                new_race = {
                    "race_date": new_race_date,
                    "race_type": new_race_type,
                    "distance": new_race_distance,
                    "target_pace": new_race_pace,
                    "target_pace_str": format_pace(new_race_pace) if new_race_pace else "",
                    "objective": new_race_objective
                }

                # Ajouter à la liste des courses intermédiaires
                st.session_state.intermediate_races.append(new_race)
                st.success(translate("race_added", "forms") or "Course intermédiaire ajoutée avec succès.")
                st.rerun()

    # Traitement du formulaire après soumission
    if submit_button:
        # Collecter les données du formulaire
        form_data = {
            "start_date": start_date,
            "race_date": race_date,
            "race_type": race_type,
            "sessions_per_week": sessions,
            "min_volume": min_volume,
            "max_volume": max_volume,
            "intermediate_races": st.session_state.intermediate_races
        }

        # Ajouter les champs spécifiques si nécessaire
        if race_type == RaceType.OTHER.value:
            if distance is not None:
                form_data["distance"] = distance

            if target_time is not None:
                form_data["target_time"] = target_time
                # Décomposer pour faciliter la sauvegarde
                form_data["target_time_hours"] = target_time.seconds // 3600
                form_data["target_time_minutes"] = (target_time.seconds % 3600) // 60
                form_data["target_time_seconds"] = target_time.seconds % 60

        # Ajouter les allures
        if pace_5k:
            form_data["pace_5k"] = pace_5k
            form_data["pace_5k_str"] = format_pace(pace_5k)

        if pace_10k:
            form_data["pace_10k"] = pace_10k
            form_data["pace_10k_str"] = format_pace(pace_10k)

        if pace_half:
            form_data["pace_half_marathon"] = pace_half
            form_data["pace_half_str"] = format_pace(pace_half)

        if pace_marathon:
            form_data["pace_marathon"] = pace_marathon
            form_data["pace_marathon_str"] = format_pace(pace_marathon)

        # Traiter les données
        success, message, user_data = input_controller.process_form_data(form_data)

        if success:
            # Sauvegarder les entrées utilisateur
            input_controller.save_input(form_data)

            # Stocker les données utilisateur dans la session
            st.session_state["user_data"] = user_data
            
            # Marquer comme prêt pour la génération d'un nouveau plan
            st.session_state["regenerate_plan"] = True
            
            # Assurer que les boutons de navigation seront activés
            st.session_state["plan_generated"] = True

            # Afficher un message de succès avant de rediriger
            st.success(translate("plan_generation_success", "input_page") or "Plan d'entraînement généré avec succès!")

            # Passer à la page du plan
            st.session_state["page"] = "plan_view"
            st.rerun()
        else:
            # Afficher le message d'erreur
            st.error(message)

    # Traitement de la sauvegarde des allures uniquement
    elif save_paces:
        # Collecter uniquement les données d'allure
        paces_data = {}

        if pace_5k:
            paces_data["pace_5k"] = pace_5k
            paces_data["pace_5k_str"] = format_pace(pace_5k)

        if pace_10k:
            paces_data["pace_10k"] = pace_10k
            paces_data["pace_10k_str"] = format_pace(pace_10k)

        if pace_half:
            paces_data["pace_half_marathon"] = pace_half
            paces_data["pace_half_str"] = format_pace(pace_half)

        if pace_marathon:
            paces_data["pace_marathon"] = pace_marathon
            paces_data["pace_marathon_str"] = format_pace(pace_marathon)

        # Si des allures valides sont fournies
        if paces_data:
            # Récupérer les entrées existantes
            existing_data = input_controller.load_input()

            # Mettre à jour avec les nouvelles allures
            existing_data.update(paces_data)

            # Sauvegarder
            input_controller.save_input(existing_data)

            st.success(translate("paces_saved", "input_page") or "Vos allures ont été enregistrées avec succès.")