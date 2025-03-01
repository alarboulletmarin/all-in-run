"""
Page de saisie des données utilisateur.
"""
import streamlit as st
from datetime import date, timedelta
from typing import Dict, List, Any, Optional

from controllers.input_controller import InputController
from models.course import RaceType
from utils.date_utils import get_next_monday, get_sunday
from utils.time_converter import parse_time_string, parse_pace_string, format_pace
from utils.i18n import _
from config.constants import (
    MIN_WEEKS_BEFORE_RACE,
    MIN_SESSIONS_PER_WEEK,
    MAX_SESSIONS_PER_WEEK,
    DEFAULT_MIN_VOLUME,
    DEFAULT_MAX_VOLUME,
    DEFAULT_SESSIONS_PER_WEEK
)
from ui.components import (
    render_date_selector,
    render_pace_input,
    render_time_input,
    render_race_type_selector,
    render_sessions_per_week_selector,
    render_volume_inputs,
    render_intermediate_race_form,
    create_paces_summary
)


def render_input_form(input_controller: InputController):
    """
    Affiche le formulaire de saisie des données utilisateur

    Args:
        input_controller: Contrôleur de saisie
    """
    st.title(_("create_plan_title", "input_page"))

    # Charger les entrées précédentes si disponibles
    saved_input = input_controller.load_input()

    # Initialiser les courses intermédiaires
    if "intermediate_races" not in st.session_state:
        st.session_state.intermediate_races = saved_input.get("intermediate_races", [])

    # Gérer l'ajout de course intermédiaire (en dehors du formulaire)
    st.subheader(_("intermediate_races", "input_page"))

    # Afficher les courses intermédiaires existantes
    for i, race in enumerate(st.session_state.intermediate_races):
        # Utiliser des expanders pour chaque course
        with st.expander(f"{_('intermediate_race', 'forms')} {i + 1}", expanded=True):
            col1, col2 = st.columns([3, 1])

            with col1:
                st.write(f"Date: {race.get('race_date', date.today())}")
                st.write(f"Type: {race.get('race_type', RaceType.TEN_K.value)}")

            with col2:
                # Le bouton de suppression est en dehors du formulaire
                if st.button(f"{_('delete_race', 'forms')} {i + 1}", key=f"delete_race_{i}"):
                    st.session_state.intermediate_races.pop(i)
                    st.rerun()

    # Bouton pour ajouter une course intermédiaire (en dehors du formulaire)
    if st.button(_("add_intermediate_race", "input_page")):
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

        # Ajouter une nouvelle course intermédiaire
        st.session_state.intermediate_races.append({
            "race_date": default_date,
            "race_type": RaceType.TEN_K.value
        })
        st.rerun()

    # Formulaire principal
    with st.form(key="user_data_form"):
        st.header(_("race_info", "input_page"))

        col1, col2 = st.columns(2)

        with col1:
            race_type = render_race_type_selector(
                label=_("race_type", "input_page"),
                key="race_type",
                default_value=saved_input.get("race_type", RaceType.TEN_K.value)
            )

            # Champs spécifiques pour le type "autre"
            distance = None
            target_time = None

            if race_type == RaceType.OTHER.value:
                distance = st.number_input(
                    label=_("race_distance", "input_page"),
                    min_value=1.0,
                    max_value=100.0,
                    value=saved_input.get("distance", 10.0),
                    step=0.1,
                    key="distance"
                )

                target_time = render_time_input(
                    label=_("race_target_time", "input_page"),
                    key="target_time",
                    default_hours=saved_input.get("target_time_hours", 0),
                    default_minutes=saved_input.get("target_time_minutes", 45),
                    default_seconds=saved_input.get("target_time_seconds", 0)
                )

        with col2:
            # Dates de début et de course
            today = date.today()

            start_date = render_date_selector(
                label=_("start_date", "input_page"),
                key="start_date",
                default_value=saved_input.get("start_date", get_next_monday(today)),
                min_value=today,
                required_weekday=0,  # Lundi
                help_text=_("start_date_help", "input_page")
            )

            min_race_date = start_date + timedelta(days=MIN_WEEKS_BEFORE_RACE * 7)

            race_date = render_date_selector(
                label=_("race_date", "input_page"),
                key="race_date",
                default_value=saved_input.get("race_date", get_sunday(min_race_date)),
                min_value=min_race_date,
                required_weekday=6,  # Dimanche
                help_text=_("race_date_help", "input_page")
            )

            # Vérifier l'écart entre les dates
            days_diff = (race_date - start_date).days
            weeks_diff = days_diff // 7

            if weeks_diff < MIN_WEEKS_BEFORE_RACE:
                st.warning(
                    _("min_weeks_warning", "input_page").format(
                        weeks=MIN_WEEKS_BEFORE_RACE
                    )
                )
            else:
                st.success(
                    _("plan_duration", "input_page").format(
                        weeks=weeks_diff
                    )
                )

        st.header(_("user_paces", "input_page"))

        col1, col2 = st.columns(2)

        with col1:
            pace_5k = render_pace_input(
                label=_("pace_5k", "input_page"),
                key="pace_5k",
                default_value=saved_input.get("pace_5k_str", "04:30")
            )

            pace_half = render_pace_input(
                label=_("pace_half", "input_page"),
                key="pace_half",
                default_value=saved_input.get("pace_half_str", "05:00")
            )

        with col2:
            pace_10k = render_pace_input(
                label=_("pace_10k", "input_page"),
                key="pace_10k",
                default_value=saved_input.get("pace_10k_str", "04:45")
            )

            pace_marathon = render_pace_input(
                label=_("pace_marathon", "input_page"),
                key="pace_marathon",
                default_value=saved_input.get("pace_marathon_str", "05:30")
            )

        # Vérifier l'ordre des allures
        if all([pace_5k, pace_10k, pace_half, pace_marathon]):
            if not (pace_5k < pace_10k < pace_half < pace_marathon):
                st.warning(_("pace_order_warning", "input_page"))

        st.header(_("training_params", "input_page"))

        col1, col2 = st.columns(2)

        with col1:
            sessions = render_sessions_per_week_selector(
                label=_("sessions_per_week", "input_page"),
                key="sessions_per_week",
                default_value=saved_input.get("sessions_per_week", DEFAULT_SESSIONS_PER_WEEK),
                help_text=_("sessions_per_week_help", "input_page")
            )

        with col2:
            min_volume, max_volume = render_volume_inputs(
                min_label=_("min_volume", "input_page"),
                max_label=_("max_volume", "input_page"),
                min_key="min_volume",
                max_key="max_volume",
                default_min=saved_input.get("min_volume", DEFAULT_MIN_VOLUME),
                default_max=saved_input.get("max_volume", DEFAULT_MAX_VOLUME),
                help_text=_("volume_help", "input_page")
            )

        # Rappel de configuration des courses intermédiaires
        st.info(_("intermediate_races", "input_page") + " : " +
                str(len(st.session_state.intermediate_races)) + " " +
                _("courses configurées", "input_page"))

        # Bouton de soumission
        submit_button = st.form_submit_button(_("generate_plan", "input_page"))

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

            # Passer à la page du plan
            st.session_state["page"] = "plan_view"
            st.rerun()
        else:
            # Afficher le message d'erreur
            st.error(message)