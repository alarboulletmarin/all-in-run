"""
Composants de visualisation graphique pour l'interface utilisateur.
"""
import streamlit as st
from datetime import date, timedelta, datetime
from typing import Dict, List, Any, Optional, Tuple
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

from models.plan import TrainingPlan
from models.session import Session, SessionType, TrainingPhase
from utils.time_converter import format_timedelta, format_pace
from utils.i18n import _
from config.languages import PHASE_TRANSLATIONS, SESSION_TYPE_TRANSLATIONS


def render_volume_chart(
        plan: TrainingPlan,
        lang: str = "fr",
        current_week: Optional[int] = None
) -> None:
    """
    Affiche un graphique de l'évolution du volume hebdomadaire

    Args:
        plan: Plan d'entraînement
        lang: Code de langue
        current_week: Numéro de la semaine actuelle (pour mise en évidence)
    """
    # Préparation des données
    weeks = sorted(plan.weekly_volumes.keys())
    volumes = [plan.weekly_volumes[week] for week in weeks]

    # Convertir en numéros de semaine (1-based)
    week_numbers = [week + 1 for week in weeks]

    # Créer un DataFrame
    data = pd.DataFrame({
        "week": week_numbers,
        "volume": volumes
    })

    # Créer le graphique
    fig = px.bar(
        data,
        x="week",
        y="volume",
        labels={
            "week": _("week_number", "charts"),
            "volume": _("volume_km", "charts")
        },
        title=_("weekly_volume_evolution", "charts")
    )

    # Ajouter une ligne de tendance
    fig.add_trace(
        go.Scatter(
            x=data["week"],
            y=data["volume"].rolling(window=3, min_periods=1).mean(),
            mode="lines",
            name=_("trend", "charts"),
            line=dict(color="red", width=2, dash="dash")
        )
    )

    # Mettre en évidence la semaine actuelle si spécifiée
    if current_week is not None and current_week + 1 in week_numbers:
        current_volume = data[data["week"] == current_week + 1]["volume"].values[0]

        fig.add_trace(
            go.Scatter(
                x=[current_week + 1],
                y=[current_volume],
                mode="markers",
                marker=dict(color="green", size=12, symbol="circle"),
                name=_("current_week", "charts")
            )
        )

    # Mise en forme
    fig.update_layout(
        xaxis=dict(
            tickmode="linear",
            tick0=1,
            dtick=1,
            title=_("week", "charts")
        ),
        yaxis=dict(
            title=_("volume_km", "charts")
        ),
        hovermode="closest"
    )

    # Afficher le graphique
    st.plotly_chart(fig, use_container_width=True)


def render_session_type_distribution(
        plan: TrainingPlan,
        lang: str = "fr"
) -> None:
    """
    Affiche un graphique de la répartition des types de séances

    Args:
        plan: Plan d'entraînement
        lang: Code de langue
    """
    # Compter les séances par type
    session_types = {}
    for session in plan.sessions.values():
        if session.session_type != SessionType.REST:
            session_type = session.session_type.value
            session_types[session_type] = session_types.get(session_type, 0) + 1

    if not session_types:
        st.warning(_("no_data_available", "charts"))
        return

    translated_types = {}
    for session_type, count in session_types.items():
        translated_type = SESSION_TYPE_TRANSLATIONS.get(lang, {}).get(
            session_type, session_type
        )
        translated_types[translated_type] = count

    # Créer le graphique en camembert
    fig = go.Figure(data=[
        go.Pie(
            labels=list(translated_types.keys()),
            values=list(translated_types.values()),
            hole=0.4
        )
    ])

    fig.update_layout(
        title=_("session_type_distribution", "charts")
    )

    # Afficher le graphique
    st.plotly_chart(fig, use_container_width=True)


def render_phase_volume_distribution(
        plan: TrainingPlan,
        lang: str = "fr"
) -> None:
    """
    Affiche un graphique de la répartition du volume par phase

    Args:
        plan: Plan d'entraînement
        lang: Code de langue
    """
    # Calculer le volume par phase
    phase_stats = plan.get_phase_stats()

    if not phase_stats:
        st.warning(_("no_data_available", "charts"))
        return

    # Préparer les données
    phases = []
    volumes = []

    for phase, stats in phase_stats.items():
        phase_name = PHASE_TRANSLATIONS.get(lang, {}).get(
            phase.value, phase.value
        )
        phases.append(phase_name)
        volumes.append(stats["total_volume"])

    # Créer le graphique
    fig = go.Figure(data=[
        go.Bar(
            x=phases,
            y=volumes,
            text=volumes,
            textposition="auto"
        )
    ])

    fig.update_layout(
        title=_("volume_by_phase", "charts"),
        xaxis_title=_("phase", "charts"),
        yaxis_title=_("volume_km", "charts")
    )

    # Afficher le graphique
    st.plotly_chart(fig, use_container_width=True)


def render_training_load_chart(
        plan: TrainingPlan,
        lang: str = "fr",
        current_week: Optional[int] = None
) -> None:
    """
    Affiche un graphique de la charge d'entraînement

    Args:
        plan: Plan d'entraînement
        lang: Code de langue
        current_week: Numéro de la semaine actuelle (pour mise en évidence)
    """
    # Calculer la charge d'entraînement par semaine
    # La charge est une estimation basée sur le volume et l'intensité
    sessions_by_week = plan.get_sessions_by_week()

    weeks = sorted(sessions_by_week.keys())
    loads = []

    for week in weeks:
        week_sessions = sessions_by_week[week]

        # Somme des scores de difficulté pondérés par la distance
        total_distance = sum(s.total_distance for s in week_sessions
                             if s.session_type != SessionType.REST)

        if total_distance > 0:
            load = sum(s.get_difficulty_score() * (s.total_distance / total_distance)
                       for s in week_sessions if s.total_distance > 0)
            loads.append(load * total_distance / 10)  # Normaliser
        else:
            loads.append(0)

    # Convertir en numéros de semaine (1-based)
    week_numbers = [week + 1 for week in weeks]

    # Créer un DataFrame
    data = pd.DataFrame({
        "week": week_numbers,
        "load": loads
    })

    # Créer le graphique
    fig = px.line(
        data,
        x="week",
        y="load",
        markers=True,
        labels={
            "week": _("week_number", "charts"),
            "load": _("training_load", "charts")
        },
        title=_("training_load_evolution", "charts")
    )

    # Ajouter une ligne de tendance
    fig.add_trace(
        go.Scatter(
            x=data["week"],
            y=data["load"].rolling(window=3, min_periods=1).mean(),
            mode="lines",
            name=_("trend", "charts"),
            line=dict(color="green", width=2, dash="dash")
        )
    )

    # Mettre en évidence la semaine actuelle si spécifiée
    if current_week is not None and current_week + 1 in week_numbers:
        current_load = data[data["week"] == current_week + 1]["load"].values[0]

        fig.add_trace(
            go.Scatter(
                x=[current_week + 1],
                y=[current_load],
                mode="markers",
                marker=dict(color="red", size=12, symbol="circle"),
                name=_("current_week", "charts")
            )
        )

    # Mise en forme
    fig.update_layout(
        xaxis=dict(
            tickmode="linear",
            tick0=1,
            dtick=1,
            title=_("week", "charts")
        ),
        yaxis=dict(
            title=_("load_units", "charts")
        ),
        hovermode="closest"
    )

    # Afficher le graphique
    st.plotly_chart(fig, use_container_width=True)


def render_weekly_distance_by_type(
        plan: TrainingPlan,
        week_num: int,
        lang: str = "fr"
) -> None:
    """
    Affiche un graphique de la répartition du volume par type de séance pour une semaine

    Args:
        plan: Plan d'entraînement
        week_num: Numéro de la semaine
        lang: Code de langue
    """
    # Récupérer les séances de la semaine
    sessions_by_week = plan.get_sessions_by_week()

    if week_num not in sessions_by_week:
        st.warning(_("no_data_available", "charts"))
        return

    # Calculer la distance par type de séance
    session_types = {}
    for session in sessions_by_week[week_num]:
        if session.session_type != SessionType.REST:
            session_type = session.session_type.value
            translated_type = _("session_type_" + session_type.lower().replace(" ", "_"), "session_types")
            session_types[translated_type] = session_types.get(translated_type, 0) + session.total_distance

    if not session_types:
        st.warning(_("no_data_available", "charts"))
        return

    # Créer le graphique
    fig = go.Figure(data=[
        go.Pie(
            labels=list(session_types.keys()),
            values=list(session_types.values()),
            hole=0.4,
            textinfo="label+percent",
            hoverinfo="label+value"
        )
    ])

    fig.update_layout(
        title=_("weekly_distance_by_type", "charts")
    )

    # Afficher le graphique
    st.plotly_chart(fig, use_container_width=True)


def render_intensity_distribution(
        plan: TrainingPlan,
        lang: str = "fr"
) -> None:
    """
    Affiche un graphique de la répartition des intensités d'entraînement

    Args:
        plan: Plan d'entraînement
        lang: Code de langue
    """
    # Calculer le temps passé à différentes intensités
    intensity_bins = {
        _("recovery", "intensity"): timedelta(0),
        _("easy", "intensity"): timedelta(0),
        _("moderate", "intensity"): timedelta(0),
        _("threshold", "intensity"): timedelta(0),
        _("interval", "intensity"): timedelta(0),
        _("race", "intensity"): timedelta(0)
    }

    for session in plan.sessions.values():
        if session.session_type == SessionType.REST:
            continue

        for block in session.blocks:
            # Classer l'intensité en fonction de l'allure
            pace_seconds = block.pace.total_seconds()
            duration = block.duration

            if pace_seconds > 390:  # > 6:30/km
                intensity_bins[_("recovery", "intensity")] += duration
            elif pace_seconds > 330:  # 5:30-6:30/km
                intensity_bins[_("easy", "intensity")] += duration
            elif pace_seconds > 270:  # 4:30-5:30/km
                intensity_bins[_("moderate", "intensity")] += duration
            elif pace_seconds > 240:  # 4:00-4:30/km
                intensity_bins[_("threshold", "intensity")] += duration
            elif pace_seconds > 210:  # 3:30-4:00/km
                intensity_bins[_("interval", "intensity")] += duration
            else:  # < 3:30/km
                intensity_bins[_("race", "intensity")] += duration

    # Convertir en heures pour l'affichage
    intensity_hours = {
        zone: duration.total_seconds() / 3600
        for zone, duration in intensity_bins.items()
        if duration.total_seconds() > 0
    }

    if not intensity_hours:
        st.warning(_("no_data_available", "charts"))
        return

    # Créer le graphique
    fig = go.Figure(data=[
        go.Bar(
            x=list(intensity_hours.keys()),
            y=list(intensity_hours.values()),
            text=[f"{hours:.1f}h" for hours in intensity_hours.values()],
            textposition="auto"
        )
    ])

    fig.update_layout(
        title=_("intensity_distribution", "charts"),
        xaxis_title=_("intensity_zone", "charts"),
        yaxis_title=_("hours", "charts")
    )

    # Afficher le graphique
    st.plotly_chart(fig, use_container_width=True)


def render_comparison_chart(
        original_plan: TrainingPlan,
        simulated_plan: TrainingPlan,
        metric: str = "volume",  # volume, intensity, sessions
        lang: str = "fr"
) -> None:
    """
    Affiche un graphique comparant deux plans d'entraînement

    Args:
        original_plan: Plan d'entraînement original
        simulated_plan: Plan d'entraînement simulé
        metric: Métrique à comparer (volume, intensity, sessions)
        lang: Code de langue
    """
    if metric == "volume":
        # Comparer les volumes hebdomadaires
        original_weeks = sorted(original_plan.weekly_volumes.keys())
        original_volumes = [original_plan.weekly_volumes[week] for week in original_weeks]

        simulated_weeks = sorted(simulated_plan.weekly_volumes.keys())
        simulated_volumes = [simulated_plan.weekly_volumes[week] for week in simulated_weeks]

        # Créer un DataFrame pour la comparaison
        data = pd.DataFrame({
            "week": [week + 1 for week in range(max(max(original_weeks), max(simulated_weeks)) + 1)],
            _("original", "charts"): pd.Series(
                original_volumes,
                index=[week + 1 for week in original_weeks]
            ),
            _("simulated", "charts"): pd.Series(
                simulated_volumes,
                index=[week + 1 for week in simulated_weeks]
            )
        }).fillna(0)

        # Créer le graphique
        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=data["week"],
                y=data[_("original", "charts")],
                name=_("original", "charts"),
                marker_color="blue",
                opacity=0.7
            )
        )

        fig.add_trace(
            go.Bar(
                x=data["week"],
                y=data[_("simulated", "charts")],
                name=_("simulated", "charts"),
                marker_color="green",
                opacity=0.7
            )
        )

        fig.update_layout(
            title=_("volume_comparison", "charts"),
            xaxis_title=_("week", "charts"),
            yaxis_title=_("volume_km", "charts"),
            barmode="group"
        )

    elif metric == "intensity":
        # Comparer l'intensité (calculer un score moyen par semaine)
        original_intensity = []
        simulated_intensity = []
        weeks = []

        max_week = max(
            max(original_plan.weekly_volumes.keys()),
            max(simulated_plan.weekly_volumes.keys())
        )

        for week in range(max_week + 1):
            original_sessions = [s for s in original_plan.sessions.values()
                                 if (s.session_date - original_plan.user_data.start_date).days // 7 == week]

            simulated_sessions = [s for s in simulated_plan.sessions.values()
                                  if (s.session_date - simulated_plan.user_data.start_date).days // 7 == week]

            # Calculer l'intensité moyenne (score de difficulté normalisé)
            original_total_distance = sum(s.total_distance for s in original_sessions
                                          if s.session_type != SessionType.REST)

            simulated_total_distance = sum(s.total_distance for s in simulated_sessions
                                           if s.session_type != SessionType.REST)

            if original_total_distance > 0:
                original_score = sum(s.get_difficulty_score() * (s.total_distance / original_total_distance)
                                     for s in original_sessions if s.total_distance > 0)
                original_intensity.append(original_score)
            else:
                original_intensity.append(0)

            if simulated_total_distance > 0:
                simulated_score = sum(s.get_difficulty_score() * (s.total_distance / simulated_total_distance)
                                      for s in simulated_sessions if s.total_distance > 0)
                simulated_intensity.append(simulated_score)
            else:
                simulated_intensity.append(0)

            weeks.append(week + 1)

        # Créer un DataFrame pour la comparaison
        data = pd.DataFrame({
            "week": weeks,
            _("original", "charts"): original_intensity,
            _("simulated", "charts"): simulated_intensity
        })

        # Créer le graphique
        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=data["week"],
                y=data[_("original", "charts")],
                mode="lines+markers",
                name=_("original", "charts"),
                line=dict(color="blue", width=2)
            )
        )

        fig.add_trace(
            go.Scatter(
                x=data["week"],
                y=data[_("simulated", "charts")],
                mode="lines+markers",
                name=_("simulated", "charts"),
                line=dict(color="green", width=2)
            )
        )

        fig.update_layout(
            title=_("intensity_comparison", "charts"),
            xaxis_title=_("week", "charts"),
            yaxis_title=_("intensity_score", "charts")
        )

    else:  # sessions
        # Comparer le nombre de séances par type
        from .config.languages import SESSION_TYPE_TRANSLATIONS

        original_types = {}
        for session in original_plan.sessions.values():
            if session.session_type != SessionType.REST:
                session_type = session.session_type.value
                translated_type = SESSION_TYPE_TRANSLATIONS.get(lang, {}).get(
                    session_type, session_type
                )
                original_types[translated_type] = original_types.get(translated_type, 0) + 1

        simulated_types = {}
        for session in simulated_plan.sessions.values():
            if session.session_type != SessionType.REST:
                session_type = session.session_type.value
                translated_type = SESSION_TYPE_TRANSLATIONS.get(lang, {}).get(
                    session_type, session_type
                )
                simulated_types[translated_type] = simulated_types.get(translated_type, 0) + 1

        # Combiner les types pour avoir le même ensemble dans les deux plans
        all_types = set(original_types.keys()) | set(simulated_types.keys())
        original_counts = [original_types.get(t, 0) for t in all_types]
        simulated_counts = [simulated_types.get(t, 0) for t in all_types]

        # Créer le graphique
        fig = go.Figure(data=[
            go.Bar(
                name=_("original", "charts"),
                x=list(all_types),
                y=original_counts,
                marker_color="blue"
            ),
            go.Bar(
                name=_("simulated", "charts"),
                x=list(all_types),
                y=simulated_counts,
                marker_color="green"
            )
        ])

        fig.update_layout(
            title=_("session_count_comparison", "charts"),
            xaxis_title=_("session_type", "charts"),
            yaxis_title=_("count", "charts"),
            barmode="group"
        )

    # Afficher le graphique
    st.plotly_chart(fig, use_container_width=True)