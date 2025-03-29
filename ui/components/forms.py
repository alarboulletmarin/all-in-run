import streamlit as st
from datetime import date, timedelta
from typing import Dict, Any, Optional, Tuple, Callable

from config import DATE_FORMAT
from utils.date_utils import get_next_monday, get_sunday
from utils.time_converter import parse_pace_string, format_timedelta, format_pace
from utils.i18n import _ as translate
from models.course import RaceType
from config.constants import (
    MIN_SESSIONS_PER_WEEK,
    MAX_SESSIONS_PER_WEEK,
    DEFAULT_MIN_VOLUME,
    DEFAULT_MAX_VOLUME,
    DEFAULT_SESSIONS_PER_WEEK
)


def render_date_selector(
        label: str,
        key: str,
        default_value: date = None,
        min_value: date = None,
        max_value: date = None,
        help_text: str = None,
        required_weekday: Optional[int] = None,
        on_change: Optional[Callable] = None,
        strict_weekday: bool = False
) -> date:
    """
    Affiche un sélecteur de date avec validation du jour de la semaine

    Args:
        label: Libellé du champ
        key: Clé unique pour le champ
        default_value: Valeur par défaut
        min_value: Valeur minimale
        max_value: Valeur maximale
        help_text: Texte d'aide
        required_weekday: Jour de la semaine requis (0=lundi, 6=dimanche)
        on_change: Fonction à appeler lors du changement
        strict_weekday: Si True, force le jour de la semaine requis

    Returns:
        Date sélectionnée
    """
    # Si aucune valeur par défaut n'est fournie, utiliser la date du jour
    if default_value is None:
        default_value = date.today()

    # Afficher le sélecteur de date
    selected_date = st.date_input(
        label=label,
        value=default_value,
        min_value=min_value,
        max_value=max_value,
        key=key,
        help=help_text,
        on_change=on_change,
        format=DATE_FORMAT
    )

    # Vérifier le jour de la semaine si nécessaire
    if required_weekday is not None and selected_date.weekday() != required_weekday:
        weekday_names = {
            0: translate("monday", "common"),
            6: translate("sunday", "common")
        }

        message = translate("date_needs_to_be_weekday", "forms").format(
            weekday=weekday_names.get(required_weekday, str(required_weekday))
        )

        if strict_weekday:
            # Erreur bloquante
            st.error(message)

            # Ajuster automatiquement la date
            if required_weekday == 0:  # Lundi
                adjusted_date = get_next_monday(selected_date)
            elif required_weekday == 6:  # Dimanche
                adjusted_date = get_sunday(selected_date)
            else:
                adjusted_date = selected_date

            # Forcer la mise à jour de la date
            st.session_state[key] = adjusted_date
            st.rerun()
            return adjusted_date
        else:
            # Simple avertissement
            st.warning(message)

            # Ajuster automatiquement la date si nécessaire
            if required_weekday == 0:  # Lundi
                adjusted_date = get_next_monday(selected_date)
                if adjusted_date != selected_date:
                    st.session_state[key] = adjusted_date
                    return adjusted_date
            elif required_weekday == 6:  # Dimanche
                adjusted_date = get_sunday(selected_date)
                if adjusted_date != selected_date:
                    st.session_state[key] = adjusted_date
                    return adjusted_date

    return selected_date


def render_pace_input(
        label: str,
        key: str,
        default_value: str = "05:00",
        help_text: str = None
) -> Optional[timedelta]:
    """
    Affiche un champ de saisie d'allure (min:sec par km)

    Args:
        label: Libellé du champ
        key: Clé unique pour le champ
        default_value: Valeur par défaut
        help_text: Texte d'aide

    Returns:
        Allure sous forme de timedelta ou None si invalide
    """
    pace_str = st.text_input(
        label=label,
        value=default_value,
        key=key,
        help=help_text or translate("pace_format_help", "forms"),
        placeholder="mm:ss"
    )

    # Valider et convertir l'allure
    pace = parse_pace_string(pace_str)

    # Afficher un message d'erreur si l'allure est invalide
    if pace_str and pace is None:
        st.error(translate("invalid_pace_format", "forms"))

    return pace


def render_time_input(
        label: str,
        key: str,
        default_hours: int = 0,
        default_minutes: int = 0,
        default_seconds: int = 0,
        help_text: str = None
) -> Optional[timedelta]:
    """
    Affiche un ensemble de champs pour saisir un temps (heures, minutes, secondes)

    Args:
        label: Libellé du champ
        key: Clé unique pour le champ
        default_hours: Heures par défaut
        default_minutes: Minutes par défaut
        default_seconds: Secondes par défaut
        help_text: Texte d'aide

    Returns:
        Temps sous forme de timedelta ou None si invalide
    """
    st.write(label)

    col1, col2, col3 = st.columns(3)

    with col1:
        hours = st.number_input(
            translate("hours", "common"),
            min_value=0,
            max_value=24,
            value=default_hours,
            key=f"{key}_hours"
        )

    with col2:
        minutes = st.number_input(
            translate("minutes", "common"),
            min_value=0,
            max_value=59,
            value=default_minutes,
            key=f"{key}_minutes"
        )

    with col3:
        seconds = st.number_input(
            translate("seconds", "common"),
            min_value=0,
            max_value=59,
            value=default_seconds,
            key=f"{key}_seconds"
        )

    if help_text:
        st.info(help_text)

    # Créer le timedelta
    if hours == 0 and minutes == 0 and seconds == 0:
        return None

    return timedelta(hours=hours, minutes=minutes, seconds=seconds)


def render_race_type_selector(
        label: str,
        key: str,
        default_value: str = "10K",
        on_change: Optional[Callable] = None
) -> str:
    """
    Affiche un sélecteur de type de course

    Args:
        label: Libellé du champ
        key: Clé unique pour le champ
        default_value: Valeur par défaut
        on_change: Fonction à appeler lors du changement

    Returns:
        Type de course sélectionné
    """
    race_types = [
        RaceType.TEN_K.value,
        RaceType.HALF_MARATHON.value,
        RaceType.MARATHON.value,
        RaceType.OTHER.value
    ]

    translated_types = [translate(rt, "race_types") for rt in race_types]

    # Trouver l'index de la valeur par défaut
    try:
        default_index = race_types.index(default_value)
    except ValueError:
        default_index = 0

    selected_type = st.selectbox(
        label=label,
        options=race_types,
        index=default_index,
        format_func=lambda x: translate(x, "race_types"),
        key=key,
        on_change=on_change
    )

    return selected_type


def render_sessions_per_week_selector(
        label: str,
        key: str,
        default_value: int = DEFAULT_SESSIONS_PER_WEEK,
        help_text: str = None
) -> int:
    """
    Affiche un sélecteur du nombre de séances par semaine

    Args:
        label: Libellé du champ
        key: Clé unique pour le champ
        default_value: Valeur par défaut
        help_text: Texte d'aide

    Returns:
        Nombre de séances par semaine
    """
    sessions = st.slider(
        label=label,
        min_value=MIN_SESSIONS_PER_WEEK,
        max_value=MAX_SESSIONS_PER_WEEK,
        value=default_value,
        step=1,
        key=key,
        help=help_text
    )

    return sessions


def render_volume_inputs(
        min_label: str,
        max_label: str,
        min_key: str,
        max_key: str,
        default_min: float = DEFAULT_MIN_VOLUME,
        default_max: float = DEFAULT_MAX_VOLUME,
        help_text: str = None
) -> Tuple[float, float]:
    """
    Affiche des champs pour saisir les volumes min et max

    Args:
        min_label: Libellé du champ min
        max_label: Libellé du champ max
        min_key: Clé unique pour le champ min
        max_key: Clé unique pour le champ max
        default_min: Valeur min par défaut
        default_max: Valeur max par défaut
        help_text: Texte d'aide

    Returns:
        Tuple (volume min, volume max)
    """
    col1, col2 = st.columns(2)

    with col1:
        min_volume = st.number_input(
            label=min_label,
            min_value=5.0,
            max_value=300.0,
            value=default_min,
            step=5.0,
            format="%.1f",
            key=min_key
        )

    with col2:
        max_volume = st.number_input(
            label=max_label,
            min_value=min_volume + 5.0,
            max_value=300.0,
            value=max(default_max, min_volume + 5.0),
            step=5.0,
            format="%.1f",
            key=max_key
        )

    if help_text:
        st.info(help_text)

    # Vérifier que max > min
    if max_volume <= min_volume:
        st.warning(translate("volume_max_greater_than_min", "forms"))

    return min_volume, max_volume


def render_intermediate_race_form(
        index: int,
        on_delete: Callable,
        default_values: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Affiche un formulaire pour une course intermédiaire

    Args:
        index: Indice de la course
        on_delete: Fonction à appeler pour supprimer la course
        default_values: Valeurs par défaut

    Returns:
        Dictionnaire des valeurs saisies
    """
    if default_values is None:
        default_values = {}

    with st.expander(f"{translate('intermediate_race', 'forms')} {index + 1}", expanded=True):
        # Paramètres modifiables
        race_date = render_date_selector(
            label=translate("race_date", "forms"),
            key=f"intermediate_race_{index}_date",
            default_value=default_values.get(
                "race_date", date.today() + timedelta(days=30)),
            required_weekday=6,  # Dimanche
            help_text=translate("intermediate_race_date_help", "forms"),
            strict_weekday=True
        )

        race_type = render_race_type_selector(
            label=translate("race_type", "forms"),
            key=f"intermediate_race_{index}_type",
            default_value=default_values.get("race_type", RaceType.TEN_K.value)
        )

        # Distance pour les courses de type "autre"
        distance = None
        if race_type == RaceType.OTHER.value:
            distance = st.number_input(
                label=translate("race_distance", "forms"),
                min_value=1.0,
                max_value=100.0,
                value=default_values.get("distance", 10.0),
                step=0.1,
                key=f"intermediate_race_{index}_distance"
            )

        # Allure visée (avec options plus détaillées)
        target_pace = render_pace_input(
            label=translate("target_pace", "forms"),
            key=f"intermediate_race_{index}_pace",
            default_value=default_values.get("target_pace_str", "05:30")
        )

        # Objectif de la course
        race_objective = st.selectbox(
            label=translate("race_objective", "forms"),
            options=["Compétition", "Entraînement", "Test"],
            index=0,
            key=f"intermediate_race_{index}_objective"
        )

        # Note pour l'impact sur l'entraînement
        st.info(translate("race_impact_info", "forms"))

        col1, col2 = st.columns(2)

        with col1:
            # Bouton pour mettre à jour
            if st.button(translate("update_race", "forms"), key=f"update_race_{index}"):
                # Mettre à jour les données
                race_data = {
                    "race_date": race_date,
                    "race_type": race_type,
                    "distance": distance,
                    "target_pace": target_pace,
                    "target_pace_str": format_pace(target_pace) if target_pace else "",
                    "objective": race_objective
                }
                st.session_state.intermediate_races[index] = race_data
                st.success(translate("race_updated", "forms"))
                st.rerun()

        with col2:
            # Bouton de suppression
            st.button(
                translate("delete_race", "forms"),
                key=f"delete_race_{index}",
                on_click=on_delete,
                args=(index,)
            )

    # Retourner les données saisies
    race_data = {
        "race_date": race_date,
        "race_type": race_type
    }

    if distance is not None:
        race_data["distance"] = distance

    if target_pace is not None:
        race_data["target_pace"] = target_pace
        race_data["target_pace_str"] = format_pace(target_pace)

    race_data["objective"] = race_objective

    return race_data


def create_paces_summary(
        pace_5k: timedelta,
        pace_10k: timedelta,
        pace_half: timedelta,
        pace_marathon: timedelta,
        ef_pace: timedelta
) -> Dict[str, Dict[str, str]]:
    """
    Crée un résumé des allures pour affichage

    Args:
        pace_5k: Allure 5K
        pace_10k: Allure 10K
        pace_half: Allure semi-marathon
        pace_marathon: Allure marathon
        ef_pace: Allure endurance fondamentale

    Returns:
        Dictionnaire des allures formatées
    """
    paces = {
        "5K": {
            "pace": format_pace(pace_5k),
            "time": format_timedelta(pace_5k * 5, "ms")
        },
        "10K": {
            "pace": format_pace(pace_10k),
            "time": format_timedelta(pace_10k * 10, "ms")
        },
        "Half Marathon": {
            "pace": format_pace(pace_half),
            "time": format_timedelta(pace_half * 21.1, "hms")
        },
        "Marathon": {
            "pace": format_pace(pace_marathon),
            "time": format_timedelta(pace_marathon * 42.2, "hms")
        },
        "Easy": {
            "pace": format_pace(ef_pace),
            "time": "-"
        }
    }

    return paces


def render_date_with_weekday_constraint(
        label: str,
        key: str,
        required_weekday: int,  # 0=lundi, 6=dimanche
        default_value: date = None,
        min_value: date = None,
        max_value: date = None,
        help_text: str = None
) -> date:
    """
    Affiche un sélecteur de date et ajuste automatiquement la date au jour requis
    sans modifier la session state
    """
    # Ajuster la valeur par défaut si nécessaire
    if default_value is None:
        default_value = date.today()

    # S'assurer que la valeur par défaut est au bon jour de la semaine
    if default_value.weekday() != required_weekday:
        days_to_add = (required_weekday - default_value.weekday()) % 7
        default_value = default_value + timedelta(days=days_to_add)

    # Vérifier que la valeur par défaut est entre min_value et max_value
    if min_value is not None and default_value < min_value:
        # Si la valeur par défaut est trop petite, utiliser min_value
        default_value = min_value
        # Ajuster au jour de la semaine requis si nécessaire
        if default_value.weekday() != required_weekday:
            days_to_add = (required_weekday - default_value.weekday()) % 7
            default_value = default_value + timedelta(days=days_to_add)

    if max_value is not None and default_value > max_value:
        # Si la valeur par défaut est trop grande, utiliser max_value
        default_value = max_value
        # Ajuster au jour de la semaine requis si nécessaire
        if default_value.weekday() != required_weekday:
            days_to_subtract = (default_value.weekday() - required_weekday) % 7
            if days_to_subtract > 0:
                default_value = default_value - \
                    timedelta(days=days_to_subtract)

    # Clé pour stocker la date ajustée
    adjusted_key = f"{key}_adjusted"

    # Sélecteur de date standard
    selected_date = st.date_input(
        label=label,
        value=default_value,
        min_value=min_value,
        max_value=max_value,
        key=key,
        help=help_text,
        format=DATE_FORMAT
    )

    # Vérifier si la date sélectionnée est au bon jour de la semaine
    if selected_date.weekday() != required_weekday:
        weekday_name = translate(f"day_{required_weekday}", "common")
        # Calculer le prochain jour de la semaine requis
        days_to_add = (required_weekday - selected_date.weekday()) % 7
        adjusted_date = selected_date + \
            timedelta(days=(required_weekday - selected_date.weekday()) % 7)

        # Vérifier que la date ajustée est dans les limites
        if min_value is not None and adjusted_date < min_value:
            # Si on a dépassé min_value en ajustant, aller au jour requis suivant
            days_to_add += 7
            adjusted_date = selected_date + timedelta(days=days_to_add)

        if max_value is not None and adjusted_date > max_value:
            # Si on a dépassé max_value en ajustant, aller au jour requis précédent
            adjusted_date = selected_date - \
                timedelta(days=(selected_date.weekday() - required_weekday) % 7)

        # Stocker la date ajustée dans une clé différente
        st.session_state[adjusted_key] = adjusted_date

        # Afficher un message d'information
        st.warning(f"⚠️ {translate('date_needs_to_be_weekday', 'forms').format(weekday=weekday_name)}\n"
                   f"{translate('adjusted_to', 'forms')}: {adjusted_date.strftime('%d/%m/%Y')}")

        # Retourner la date ajustée
        return adjusted_date

    # Si la date est déjà au bon jour, la retourner directement
    return selected_date
