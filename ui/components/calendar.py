"""
Composants d'affichage du calendrier d'entraînement.
"""
import streamlit as st
from datetime import date, timedelta
from typing import Optional, Callable

from models.plan import TrainingPlan
from models.session import Session, SessionType, TrainingPhase
from utils.date_utils import format_date, get_week_number
from utils.time_converter import format_timedelta, format_pace, format_duration_for_calendar
from utils.i18n import _ as translate
from config.languages import DAYS_TRANSLATIONS, SESSION_TYPE_TRANSLATIONS


def render_week_navigation(
        plan: TrainingPlan,
        current_week: int,
        on_week_change: Callable[[int], None]
) -> None:
    """
    Affiche une barre de navigation pour les semaines avec un design amélioré

    Args:
        plan: Plan d'entraînement
        current_week: Numéro de la semaine actuellement affichée
        on_week_change: Fonction à appeler lors du changement de semaine
    """
    total_weeks = plan.user_data.total_weeks

    # Créer une barre de navigation plus visuelle
    st.markdown("""
    <style>
    .week-nav {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 10px 0;
        background-color: #f0f2f6;
        border-radius: 10px;
        margin-bottom: 15px;
    }
    .week-nav-title {
        text-align: center;
        flex-grow: 1;
    }
    .week-nav-dates {
        text-align: center;
        font-size: 0.9em;
        color: #565656;
    }
    .week-progress {
        height: 5px;
        background-color: #e0e0e0;
        border-radius: 5px;
        overflow: hidden;
        margin-top: 8px;
    }
    .week-progress-bar {
        height: 100%;
        background-color: #4CAF50;
    }
    @media (max-width: 640px) {
        .week-nav {
            flex-direction: column;
        }
        .week-nav-title, .week-nav-dates {
            margin: 5px 0;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 3, 1])

    with col1:
        if current_week > 0:
            st.button(
                "◀ " + translate("previous_week", "calendar"),
                key="prev_week",
                on_click=on_week_change,
                args=(current_week - 1,),
                use_container_width=True
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

        phase_str = translate(phase.value, "phases") if phase else ""

        # Calculer le pourcentage de progression
        progress_percent = min(100, int((current_week + 1) / total_weeks * 100))

        # Afficher le titre et les dates de la semaine
        st.markdown(f"""
        <div class="week-nav">
            <div class="week-nav-title">
                <h3 style="margin: 0;">{translate('week', 'calendar')} {current_week + 1}/{total_weeks} - {phase_str}</h3>
                <div class="week-nav-dates">{format_date(week_start, include_day_name=False)} - {format_date(week_end, include_day_name=False)}</div>
                <div class="week-progress">
                    <div class="week-progress-bar" style="width: {progress_percent}%"></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        if current_week < total_weeks - 1:
            st.button(
                translate("next_week", "calendar") + " ▶",
                key="next_week",
                on_click=on_week_change,
                args=(current_week + 1,),
                use_container_width=True
            )


def render_weekly_summary(
        plan: TrainingPlan,
        current_week: int,
        lang: str = "fr"
) -> None:
    """
    Affiche un résumé visuel de la semaine

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

    # Ajouter des styles CSS personnalisés
    st.markdown("""
    <style>
    .stats-container {
        display: flex;
        flex-wrap: wrap;
        gap: 15px;
        margin-bottom: 20px;
    }
    .stat-card {
        background-color: white;
        border-radius: 8px;
        padding: 15px;
        flex: 1;
        min-width: 200px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    }
    .stat-value {
        font-size: 1.8em;
        font-weight: bold;
        margin: 5px 0;
        color: #2C3E50;
    }
    .stat-label {
        color: #7F8C8D;
        font-size: 0.9em;
    }
    .session-types {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
    }
    .session-type {
        background-color: #f5f5f5;
        border-radius: 15px;
        padding: 6px 12px;
        font-size: 0.85em;
    }
    .intensity-container {
        margin-top: 10px;
    }
    .intensity-bar {
        height: 8px;
        background-color: #e0e0e0;
        border-radius: 4px;
        overflow: hidden;
    }
    .intensity-fill {
        height: 100%;
        background: linear-gradient(90deg, #4CAF50, #FFC107, #F44336);
    }
    @media (max-width: 768px) {
        .stats-container {
            flex-direction: column;
        }
        .stat-card {
            min-width: 100%;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    # Calculer l'intensité moyenne (si applicable)
    active_sessions = [s for s in sessions if s.session_type != SessionType.REST]
    intensity_percent = 0

    if active_sessions:
        total_distance = sum(s.total_distance for s in active_sessions)
        if total_distance > 0:
            avg_intensity = sum(s.get_difficulty_score() * (s.total_distance / total_distance)
                                for s in active_sessions if s.total_distance > 0)
            # Convertir en pourcentage (0-100)
            intensity_percent = min(100, int(avg_intensity * 33))

    # Afficher les statistiques dans une mise en page responsive
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label=translate('weekly_volume', 'calendar'),
            value=f"{volume} km"
        )

    with col2:
        st.metric(
            label=translate('weekly_duration', 'calendar'),
            value=format_timedelta(duration, 'hms_text')
        )

    with col3:
        st.markdown(f"**{translate('session_types', 'calendar')}**")
        for type_name, count in session_types.items():
            st.markdown(f"- {type_name}: {count}")

        st.markdown(f"**{translate('average_intensity', 'calendar')}**")
        st.progress(intensity_percent/100)  # Utilise le composant de barre de progression natif


def render_session_card(
        session: Session,
        lang: str = "fr",
        on_click: Optional[Callable[[date], None]] = None
) -> None:
    """
    Affiche une carte améliorée pour une séance

    Args:
        session: Séance à afficher
        lang: Code de langue
        on_click: Fonction à appeler lors du clic
    """
    # Déterminer la couleur de fond en fonction du type de séance
    bg_colors = {
        SessionType.LONG_RUN: "#C8E6C9",  # Vert clair
        SessionType.THRESHOLD: "#FFCDD2",  # Rouge clair
        SessionType.EF: "#B3E5FC",        # Bleu clair
        SessionType.REST: "#F5F5F5",      # Gris clair
        SessionType.RACE: "#FFF9C4"       # Jaune clair
    }

    text_colors = {
        SessionType.LONG_RUN: "#1B5E20",  # Vert foncé
        SessionType.THRESHOLD: "#B71C1C",  # Rouge foncé
        SessionType.EF: "#01579B",        # Bleu foncé
        SessionType.REST: "#424242",      # Gris foncé
        SessionType.RACE: "#F57F17"       # Jaune foncé
    }

    bg_color = bg_colors.get(session.session_type, "#FFFFFF")
    text_color = text_colors.get(session.session_type, "#000000")

    # Traduire le type de séance
    type_name = SESSION_TYPE_TRANSLATIONS.get(lang, {}).get(
        session.session_type.value,
        session.session_type.value
    )

    # Créer l'ID unique pour la carte
    card_id = f"session_card_{session.session_date.isoformat()}"

    # Créer le contenu de la carte
    if session.session_type == SessionType.REST:
        card_content = f"""
        <div id="{card_id}" class="session-card rest" style="background-color: {bg_color}; color: {text_color};">
            <div class="session-type">{type_name}</div>
            <div class="session-icon">🛌</div>
        </div>
        """
    else:
        # Choisir l'icône en fonction du type de séance
        icons = {
            SessionType.LONG_RUN: "🏃‍♂️",
            SessionType.THRESHOLD: "⚡",
            SessionType.EF: "🚶‍♂️",
            SessionType.RACE: "🏁"
        }

        icon = icons.get(session.session_type, "🏃")

        card_content = f"""
        <div id="{card_id}" class="session-card {session.session_type.value.lower().replace(' ', '-')}" 
             style="background-color: {bg_color}; color: {text_color};">
            <div class="session-type">{type_name}</div>
            <div class="session-icon">{icon}</div>
            <div class="session-details">
                <div class="session-distance">{session.total_distance} km</div>
                <div class="session-duration">{format_duration_for_calendar(session.total_duration)}</div>
            </div>
        </div>
        """

    # Ajouter le CSS pour les cartes de séance
    st.markdown("""
    <style>
    .session-card {
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 10px;
        cursor: pointer;
        transition: transform 0.2s, box-shadow 0.2s;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        min-height: 100px;
        display: flex;
        flex-direction: column;
    }
    .session-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    .session-type {
        font-weight: bold;
        margin-bottom: 5px;
    }
    .session-icon {
        font-size: 1.5em;
        margin: 5px 0;
    }
    .session-details {
        margin-top: auto;
    }
    .session-distance {
        font-weight: bold;
    }
    .session-duration {
        font-size: 0.9em;
        opacity: 0.8;
    }
    .session-card.rest {
        display: flex;
        justify-content: center;
        align-items: center;
        flex-direction: column;
    }
    .session-card.rest .session-icon {
        font-size: 2em;
        margin: 10px 0;
    }
    @media (max-width: 768px) {
        .session-card {
            padding: 8px;
            min-height: 80px;
        }
        .session-icon {
            font-size: 1.2em;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    # Afficher la carte
    st.markdown(card_content, unsafe_allow_html=True)

    # Si on_click est fourni, ajouter un bouton pour la gestion des événements
    if on_click:
        if st.button("Voir détails", key=f"btn_{card_id}", use_container_width=True):
            on_click(session.session_date)


def render_week_calendar(
        plan: TrainingPlan,
        current_week: int,
        lang: str = "fr",
        on_session_click: Optional[Callable[[date], None]] = None
) -> None:
    """
    Affiche le calendrier d'une semaine avec une mise en page responsive

    Args:
        plan: Plan d'entraînement
        current_week: Numéro de la semaine
        lang: Code de langue
        on_session_click: Fonction à appeler lors du clic sur une séance
    """
    # Calculer les dates de la semaine
    week_start, _ = plan.get_week_dates(current_week)
    week_dates = [week_start + timedelta(days=i) for i in range(7)]

    # Créer les colonnes pour chaque jour avec une mise en page responsive
    st.markdown("""
    <style>
    .days-container {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 10px;
        margin-bottom: 20px;
    }
    .day-header {
        text-align: center;
        font-weight: bold;
        padding: 10px 0;
        background-color: #f0f2f6;
        border-radius: 5px 5px 0 0;
    }
    .day-date {
        text-align: center;
        font-size: 0.9em;
        padding: 5px 0;
        background-color: #e6e6e6;
    }
    .day-content {
        padding: 10px;
        min-height: 150px;
    }
    @media (max-width: 992px) {
        .days-container {
            grid-template-columns: repeat(3, 1fr);
        }
    }
    @media (max-width: 576px) {
        .days-container {
            grid-template-columns: 1fr;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    # Créer l'en-tête pour les jours de la semaine
    day_headers = ''.join([
        f'<div class="day-header">{DAYS_TRANSLATIONS.get(lang, {}).get(i, f"Day {i}")}</div>'
        for i in range(7)
    ])

    # Créer les dates pour chaque jour
    day_dates = ''.join([
        f'<div class="day-date">{day_date.day:02d}/{day_date.month:02d}</div>'
        for day_date in week_dates
    ])

    # Créer le conteneur HTML pour les jours
    st.markdown(f"""
    <div class="days-container">
        {day_headers}
    </div>
    <div class="days-container">
        {day_dates}
    </div>
    """, unsafe_allow_html=True)

    # Utiliser des colonnes Streamlit pour les séances
    # (nécessaire pour les composants interactifs comme les boutons)
    cols = st.columns(7)

    for i, col in enumerate(cols):
        day_date = week_dates[i]
        session = plan.get_session(day_date)

        with col:
            if session:
                render_session_card(session, lang, on_session_click)
            else:
                # Espace vide pour maintenir l'alignement
                st.markdown('<div style="height: 100px;"></div>', unsafe_allow_html=True)


def render_session_details(
        session: Session,
        lang: str = "fr"
) -> None:
    """
    Affiche les détails d'une séance avec une présentation améliorée

    Args:
        session: Séance à afficher
        lang: Code de langue
    """
    # Traduire le type de séance
    type_name = SESSION_TYPE_TRANSLATIONS.get(lang, {}).get(
        session.session_type.value,
        session.session_type.value
    )

    # Couleurs par type de séance
    colors = {
        SessionType.LONG_RUN: "#43A047",  # Vert
        SessionType.THRESHOLD: "#E53935",  # Rouge
        SessionType.EF: "#039BE5",        # Bleu
        SessionType.REST: "#757575",      # Gris
        SessionType.RACE: "#FDD835"       # Jaune
    }

    color = colors.get(session.session_type, "#9E9E9E")

    # En-tête avec style
    st.markdown(f"""
    <div style="background-color: {color}; color: white; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
        <h2 style="margin:0;">{type_name}</h2>
        <div style="opacity: 0.9;">{format_date(session.session_date, lang)}</div>
    </div>
    """, unsafe_allow_html=True)

    if session.session_type == SessionType.REST:
        st.info(translate("rest_day_description", "calendar"))
        return

    # Informations générales
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label=translate("distance", "calendar"),
            value=f"{session.total_distance} km"
        )

    with col2:
        st.metric(
            label=translate("duration", "calendar"),
            value=format_timedelta(session.total_duration, 'hms_text')
        )

    with col3:
        # Calcul de l'allure moyenne
        if session.total_distance > 0:
            avg_pace = timedelta(seconds=session.total_duration.total_seconds() / session.total_distance)
            st.metric(
                label=translate("average_pace", "calendar"),
                value=format_pace(avg_pace)
            )

    # Description
    st.markdown(f"""
    <div style="background-color: #f5f5f5; padding: 15px; border-radius: 8px; margin: 20px 0;">
        <h4 style="margin-top:0;">{translate("description", "calendar")}</h4>
        <p>{session.description}</p>
    </div>
    """, unsafe_allow_html=True)

    # Détail des blocs
    if session.blocks:
        st.markdown(f"#### {translate('session_blocks', 'calendar')}")

        # CSS pour la timeline des blocs
        st.markdown("""
        <style>
        .block-timeline {
            position: relative;
            margin: 20px 0;
            padding-left: 30px;
        }
        .block-timeline::before {
            content: '';
            position: absolute;
            left: 10px;
            top: 0;
            bottom: 0;
            width: 2px;
            background-color: #e0e0e0;
        }
        .timeline-block {
            position: relative;
            margin-bottom: 15px;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .timeline-block::before {
            content: '';
            position: absolute;
            left: -25px;
            top: 20px;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background-color: #4CAF50;
        }
        .timeline-block-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
        }
        .timeline-block-title {
            font-weight: bold;
        }
        .timeline-block-stats {
            color: #666;
            font-size: 0.9em;
        }
        </style>
        """, unsafe_allow_html=True)

        # Créer la timeline des blocs
        st.markdown('<div class="block-timeline">', unsafe_allow_html=True)

        for i, block in enumerate(session.blocks, 1):
            # Couleur de fond basée sur l'intensité relative du bloc
            # Plus l'allure est rapide, plus la couleur est chaude
            base_pace = session.blocks[-1].pace.total_seconds()  # Le bloc le plus lent (souvent récup)
            relative_intensity = 1 - min(1, block.pace.total_seconds() / base_pace)

            # Couleur entre vert (0) et rouge (1)
            r = int(255 * relative_intensity)
            g = int(255 * (1 - relative_intensity))
            bg_color = f"rgba({r}, {g}, 100, 0.1)"

            st.markdown(f"""
            <div class="timeline-block" style="background-color: {bg_color};">
                <div class="timeline-block-header">
                    <div class="timeline-block-title">Bloc {i}: {block.description}</div>
                    <div class="timeline-block-stats">{block.distance} km @ {format_pace(block.pace)}</div>
                </div>
                <div>{format_timedelta(block.duration, 'ms')}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)


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

    # Préparation des données
    phases = []
    start_dates = []
    end_dates = []
    colors = []
    durations = []

    phase_colors = {
        TrainingPhase.DEVELOPMENT: "rgba(25, 118, 210, 0.7)",   # Bleu
        TrainingPhase.SPECIFIC: "rgba(56, 142, 60, 0.7)",       # Vert
        TrainingPhase.TAPER: "rgba(211, 47, 47, 0.7)"           # Rouge
    }

    for phase, stats in phase_stats.items():
        phase_name = translate(phase.value, "phases")
        phases.append(phase_name)
        start_dates.append(stats["start_date"])
        end_dates.append(stats["end_date"])
        colors.append(phase_colors.get(phase, "rgba(158, 158, 158, 0.7)"))  # Gris par défaut
        durations.append(stats["num_weeks"])

    # Créer la figure avec une présentation améliorée
    fig = go.Figure()

    for i, phase in enumerate(phases):
        # Ajouter les segments de phase
        fig.add_trace(go.Scatter(
            x=[start_dates[i], end_dates[i]],
            y=[phase, phase],
            mode="lines",
            line=dict(color=colors[i], width=20),
            name=phase,
            hovertemplate=f"{phase}<br>Début: %{{x[0]|%d %b %Y}}<br>Fin: %{{x[1]|%d %b %Y}}<br>{durations[i]} semaines",
        ))

        # Ajouter des marqueurs pour les dates de début et fin
        fig.add_trace(go.Scatter(
            x=[start_dates[i], end_dates[i]],
            y=[phase, phase],
            mode="markers",
            marker=dict(color="white", size=10, line=dict(color=colors[i], width=2)),
            showlegend=False,
            hoverinfo="skip"
        ))

    # Mettre en forme le graphique
    fig.update_layout(
        title=dict(
            text=translate("training_phases", "calendar"),
            font=dict(size=20)
        ),
        xaxis=dict(
            title=translate("date", "calendar"),
            tickformat="%d %b",
            gridcolor="rgba(0,0,0,0.1)"
        ),
        yaxis=dict(
            title=translate("phase", "calendar"),
            gridcolor="rgba(0,0,0,0.05)"
        ),
        hovermode="closest",
        height=300,
        margin=dict(l=60, r=30, t=80, b=60),
        plot_bgcolor="white",
        paper_bgcolor="white",
        showlegend=False
    )

    # Personnaliser la mise en page pour la rendre responsive
    fig.update_layout(
        autosize=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    # Afficher le graphique
    st.plotly_chart(fig, use_container_width=True, config={"responsive": True})