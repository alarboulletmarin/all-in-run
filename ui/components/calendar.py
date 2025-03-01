"""
Composants d'affichage du calendrier d'entraînement.
"""
import streamlit as st
from datetime import date, timedelta
from typing import Dict, List, Optional, Callable, Tuple
from calendar import monthrange
import pandas as pd

from models.plan import TrainingPlan
from models.session import Session, SessionType, TrainingPhase
from utils.date_utils import format_date, get_week_number, yield_month_calendar
from utils.time_converter import format_timedelta, format_pace, format_duration_for_calendar
from utils.i18n import _
from config.languages import DAYS_TRANSLATIONS, SESSION_TYPE_TRANSLATIONS


def render_week_navigation(
        plan: TrainingPlan,
        current_week: int,
        on_week_change: Callable[[int], None]
) -> None:
    """
    Affiche une barre de navigation pour les semaines

    Args:
        plan: Plan d'entraînement
        current_week: Numéro de la semaine actuellement affichée
        on_week_change: Fonction à appeler lors du changement de semaine
    """
    total_weeks = plan.user_data.total_weeks

    col1, col2, col3 = st.columns([1, 3, 1])

    with col1:
        if current_week > 0:
            st.button(
                "◀ " + _("previous_week", "calendar"),
                key="prev_week",
                on_click=on_week_change,
                args=(current_week - 1,)
            )

    with col2:
        # Calculer les dates de début et de fin de la semaine
        week_start, week_end = plan.get_week_dates(current_week)

        # Déterminer la phase de la semaine
        phase = None
        for day in range(7):
            day_date = week_start + timedelta(days=day)
            day_phase = plan.get_phase_for_date(day_date)
            if day_phase:
                phase = day_phase
                break

        phase_str = _(phase.value, "phases") if phase else ""

        # Afficher le titre de la semaine
        st.markdown(
            f"### {_('week', 'calendar')} {current_week + 1}/{total_weeks} - {phase_str}",
            unsafe_allow_html=True
        )

        # Afficher les dates de la semaine
        week_dates = f"{format_date(week_start, include_day_name=False)} - {format_date(week_end, include_day_name=False)}"
        st.markdown(f"<div style='text-align: center;'>{week_dates}</div>", unsafe_allow_html=True)

    with col3:
        if current_week < total_weeks - 1:
            st.button(
                _("next_week", "calendar") + " ▶",
                key="next_week",
                on_click=on_week_change,
                args=(current_week + 1,)
            )


def render_weekly_summary(
        plan: TrainingPlan,
        current_week: int,
        lang: str = "fr"
) -> None:
    """
    Affiche un résumé de la semaine

    Args:
        plan: Plan d'entraînement
        current_week: Numéro de la semaine
        lang: Code de langue
    """
    # Calculer le volume et la durée de la semaine
    volume = plan.get_weekly_volume(current_week)
    duration = plan.get_weekly_duration(current_week)

    # Compter les types de séances
    sessions = [s for s in plan.sessions.values()
                if get_week_number(s.session_date, plan.user_data.start_date) == current_week]

    session_types = {}
    for session in sessions:
        if session.session_type != SessionType.REST:
            type_name = SESSION_TYPE_TRANSLATIONS.get(lang, {}).get(
                session.session_type.value,
                session.session_type.value
            )
            session_types[type_name] = session_types.get(type_name, 0) + 1

    # Créer le résumé
    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            label=_("weekly_volume", "calendar"),
            value=f"{volume} km"
        )

        # Afficher les types de séances
        if session_types:
            st.write(_("session_types", "calendar"))
            for type_name, count in session_types.items():
                st.write(f"- {type_name}: {count}")

    with col2:
        st.metric(
            label=_("weekly_duration", "calendar"),
            value=format_timedelta(duration, "hms_text")
        )

        # Calculer l'intensité moyenne (si applicable)
        active_sessions = [s for s in sessions if s.session_type != SessionType.REST]
        if active_sessions:
            total_distance = sum(s.total_distance for s in active_sessions)
            avg_intensity = sum(s.get_difficulty_score() * (s.total_distance / total_distance)
                                for s in active_sessions if s.total_distance > 0)

            # Convertir en pourcentage (0-100)
            intensity_percent = min(100, int(avg_intensity * 33))

            st.metric(
                label=_("average_intensity", "calendar"),
                value=f"{intensity_percent}%"
            )


def render_week_calendar(
        plan: TrainingPlan,
        current_week: int,
        lang: str = "fr",
        on_session_click: Optional[Callable[[date], None]] = None
) -> None:
    """
    Affiche le calendrier d'une semaine

    Args:
        plan: Plan d'entraînement
        current_week: Numéro de la semaine
        lang: Code de langue
        on_session_click: Fonction à appeler lors du clic sur une séance
    """
    # Calculer les dates de la semaine
    week_start, _ = plan.get_week_dates(current_week)
    week_dates = [week_start + timedelta(days=i) for i in range(7)]

    # Créer les colonnes pour chaque jour
    cols = st.columns(7)

    # Afficher les en-têtes des jours
    for i, col in enumerate(cols):
        day_name = DAYS_TRANSLATIONS.get(lang, {}).get(i, f"Day {i}")
        with col:
            st.markdown(f"**{day_name}**")

    # Afficher les dates
    for i, col in enumerate(cols):
        day_date = week_dates[i]
        with col:
            st.markdown(f"{day_date.day:02d}/{day_date.month:02d}")

    # Afficher les séances
    for i, col in enumerate(cols):
        day_date = week_dates[i]
        session = plan.get_session(day_date)

        with col:
            if session:
                render_session_card(session, lang, on_click=on_session_click)
            else:
                # Espace vide pour maintenir l'alignement
                st.markdown("&nbsp;", unsafe_allow_html=True)


def render_session_card(
        session: Session,
        lang: str = "fr",
        on_click: Optional[Callable[[date], None]] = None
) -> None:
    """
    Affiche une carte pour une séance

    Args:
        session: Séance à afficher
        lang: Code de langue
        on_click: Fonction à appeler lors du clic
    """
    # Déterminer la couleur de fond en fonction du type de séance
    bg_colors = {
        SessionType.LONG_RUN: "#9FFFAD",  # Vert clair
        SessionType.THRESHOLD: "#FFADAD",  # Rouge clair
        SessionType.EF: "#ADFFF9",      # Bleu clair
        SessionType.REST: "#F0F0F0",     # Gris clair
        SessionType.RACE: "#FFFF7D"      # Jaune clair
    }

    bg_color = bg_colors.get(session.session_type, "#FFFFFF")

    # Traduire le type de séance
    type_name = SESSION_TYPE_TRANSLATIONS.get(lang, {}).get(
        session.session_type.value,
        session.session_type.value
    )

    # Créer le contenu de la carte
    if session.session_type == SessionType.REST:
        card_content = f"<div style='background-color: {bg_color}; padding: 10px; border-radius: 5px;'>"
        card_content += f"<b>{type_name}</b>"
        card_content += "</div>"
    else:
        card_content = f"<div style='background-color: {bg_color}; padding: 10px; border-radius: 5px;'>"
        card_content += f"<b>{type_name}</b><br>"
        card_content += f"{session.total_distance} km<br>"
        card_content += f"{format_duration_for_calendar(session.total_duration)}"
        card_content += "</div>"

    # Afficher la carte avec un bouton cliquable si on_click est fourni
    if on_click:
        if st.button(type_name, key=f"session_{session.session_date}"):
            on_click(session.session_date)
        st.markdown(card_content, unsafe_allow_html=True)
    else:
        st.markdown(card_content, unsafe_allow_html=True)


def render_month_calendar(
        plan: TrainingPlan,
        selected_year: int,
        selected_month: int,
        lang: str = "fr",
        on_date_click: Optional[Callable[[date], None]] = None,
        with_session_details: bool = True
) -> None:
    """
    Affiche un calendrier mensuel

    Args:
        plan: Plan d'entraînement
        selected_year: Année sélectionnée
        selected_month: Mois sélectionné
        lang: Code de langue
        on_date_click: Fonction à appeler lors du clic sur une date
        with_session_details: Indique si les détails des séances doivent être affichés
    """
    from .config.languages import MONTHS_TRANSLATIONS

    # Nom du mois
    month_name = MONTHS_TRANSLATIONS.get(lang, {}).get(selected_month, f"Month {selected_month}")
    st.markdown(f"## {month_name} {selected_year}")

    # En-têtes des jours
    day_headers = []
    for i in range(7):
        day_name = DAYS_TRANSLATIONS.get(lang, {}).get(i, f"Day {i}")
        day_headers.append(day_name)

    # Générer le calendrier du mois
    calendar_weeks = list(yield_month_calendar(selected_year, selected_month))

    # Créer un DataFrame pour l'affichage
    calendar_data = []

    for week in calendar_weeks:
        week_data = []
        for day in week:
            if day is None:
                # Jour hors du mois
                week_data.append("")
            else:
                # Jour dans le mois
                cell_content = str(day.day)

                # Ajouter les informations de séance si disponibles
                session = plan.get_session(day)
                if session and with_session_details:
                    if session.session_type != SessionType.REST:
                        type_name = SESSION_TYPE_TRANSLATIONS.get(lang, {}).get(
                            session.session_type.value,
                            session.session_type.value
                        )
                        cell_content += f"\n{type_name}\n{session.total_distance} km"

                week_data.append(cell_content)

        calendar_data.append(week_data)

    # Créer le DataFrame
    df = pd.DataFrame(calendar_data, columns=day_headers)

    # Afficher le calendrier
    st.dataframe(
        df,
        hide_index=True,
        use_container_width=True,
        height=min(75 * len(calendar_weeks), 450)
    )

    # TODO: Ajouter la gestion des clics sur les dates
    # Cela nécessite une approche différente car st.dataframe ne supporte pas
    # de clic interactif. On pourrait utiliser une solution alternative comme
    # st.experimental_data_editor ou un composant React personnalisé.


def render_session_details(
        session: Session,
        lang: str = "fr"
) -> None:
    """
    Affiche les détails d'une séance

    Args:
        session: Séance à afficher
        lang: Code de langue
    """
    # Traduire le type de séance
    type_name = SESSION_TYPE_TRANSLATIONS.get(lang, {}).get(
        session.session_type.value,
        session.session_type.value
    )

    # En-tête
    st.markdown(f"### {type_name} - {format_date(session.session_date, lang)}")

    if session.session_type == SessionType.REST:
        st.write(_("rest_day_description", "calendar"))
        return

    # Informations générales
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label=_("distance", "calendar"),
            value=f"{session.total_distance} km"
        )

    with col2:
        st.metric(
            label=_("duration", "calendar"),
            value=format_timedelta(session.total_duration, "hms_text")
        )

    with col3:
        # Calcul de l'allure moyenne
        if session.total_distance > 0:
            avg_pace = timedelta(seconds=session.total_duration.total_seconds() / session.total_distance)
            st.metric(
                label=_("average_pace", "calendar"),
                value=format_pace(avg_pace)
            )

    # Description
    st.markdown("#### " + _("description", "calendar"))
    st.write(session.description)

    # Détail des blocs
    if session.blocks:
        st.markdown("#### " + _("session_blocks", "calendar"))

        # Créer un tableau pour les blocs
        data = []
        for i, block in enumerate(session.blocks, 1):
            data.append({
                "#": i,
                _("distance", "calendar"): f"{block.distance} km",
                _("pace", "calendar"): format_pace(block.pace),
                _("duration", "calendar"): format_timedelta(block.duration, "ms"),
                _("description", "calendar"): block.description
            })

        # Afficher le tableau
        df = pd.DataFrame(data)
        st.table(df)


def render_phase_timeline(
        plan: TrainingPlan,
        lang: str = "fr"
) -> None:
    """
    Affiche une timeline des phases d'entraînement

    Args:
        plan: Plan d'entraînement
        lang: Code de langue
    """
    # Récupérer les statistiques des phases
    phase_stats = plan.get_phase_stats()

    if not phase_stats:
        return

    # Créer un graphique pour la timeline
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    # Préparation des données
    phases = []
    start_dates = []
    end_dates = []
    colors = []

    phase_colors = {
        TrainingPhase.DEVELOPMENT: "blue",
        TrainingPhase.SPECIFIC: "green",
        TrainingPhase.TAPER: "red"
    }

    for phase, stats in phase_stats.items():
        phase_name = _(phase.value, "phases")
        phases.append(phase_name)
        start_dates.append(stats["start_date"])
        end_dates.append(stats["end_date"])
        colors.append(phase_colors.get(phase, "gray"))

    # Créer la figure
    fig = go.Figure()

    for i, phase in enumerate(phases):
        fig.add_trace(go.Scatter(
            x=[start_dates[i], end_dates[i]],
            y=[phase, phase],
            mode="lines",
            line=dict(color=colors[i], width=20),
            name=phase
        ))

    # Mettre en forme le graphique
    fig.update_layout(
        title=_("training_phases", "calendar"),
        xaxis_title=_("date", "calendar"),
        yaxis_title=_("phase", "calendar"),
        showlegend=False
    )

    # Afficher le graphique
    st.plotly_chart(fig, use_container_width=True)