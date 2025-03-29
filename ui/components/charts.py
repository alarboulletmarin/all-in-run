import streamlit as st
from datetime import timedelta
from typing import Optional
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd

from models.plan import TrainingPlan
from models.session import SessionType, TrainingPhase
from utils.i18n import _ as translate 
from config.languages import PHASE_TRANSLATIONS, SESSION_TYPE_TRANSLATIONS

def render_volume_chart(
        plan: TrainingPlan,
        lang: str = "fr",
        current_week: Optional[int] = None
) -> None:
    """
    Affiche un graphique amélioré de l'évolution du volume hebdomadaire

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

    # Déterminer les phases pour chaque semaine
    phases = []
    colors = []

    phase_colors = {
        TrainingPhase.DEVELOPMENT: "rgba(25, 118, 210, 0.7)",   # Bleu
        TrainingPhase.SPECIFIC: "rgba(56, 142, 60, 0.7)",       # Vert
        TrainingPhase.TAPER: "rgba(211, 47, 47, 0.7)"           # Rouge
    }

    for week in weeks:
        week_start, unused = plan.get_week_dates(week)
        phase = None
        for day in range(7):
            day_date = week_start + timedelta(days=day)
            day_phase = plan.get_phase_for_date(day_date)
            if day_phase:
                phase = day_phase
                break

        # Traduire le nom de la phase
        # Import the translation function explicitly
        from utils.translations import translate
        phase_name = translate(phase.value, "phases") if phase else "Unknown"
        phases.append(phase_name)
        colors.append(phase_colors.get(phase, "rgba(158, 158, 158, 0.7)"))

    # Déterminer les "semaines de décharge" (volume inférieur à la semaine précédente)
    is_deload = [False]
    for i in range(1, len(volumes)):
        is_deload.append(volumes[i] < volumes[i-1])

    # Créer le DataFrame pour plotly
    data = pd.DataFrame({
        "week": week_numbers,
        "volume": volumes,
        "phase": phases,
        "is_deload": is_deload,
        "color": colors
    })

    # Créer le graphique avec plotly express
    fig = px.bar(
        data,
        x="week",
        y="volume",
        color="phase",
        labels={
            "week": translate("week_number", "charts"),
            "volume": translate("volume_km", "charts"),
            "phase": translate("phase", "charts")
        },
        title=translate("weekly_volume_evolution", "charts"),
        color_discrete_map={
            translate(TrainingPhase.DEVELOPMENT.value, "phases"): "rgba(25, 118, 210, 0.7)",
            translate(TrainingPhase.SPECIFIC.value, "phases"): "rgba(56, 142, 60, 0.7)",
            translate(TrainingPhase.TAPER.value, "phases"): "rgba(211, 47, 47, 0.7)"
        }
    )

    # Personnaliser les barres (semaines de décharge avec une bordure pointillée)
    for i, is_deload_week in enumerate(is_deload):
        if is_deload_week:
            # Au lieu d'utiliser update_traces avec un sélecteur, utilisons add_shape
            fig.add_shape(
                type="rect",
                # Ajuster selon la largeur des barres
                x0=week_numbers[i] - 0.4,
                x1=week_numbers[i] + 0.4,
                y0=0,
                y1=volumes[i],
                line=dict(
                    color="rgba(0, 0, 0, 0.5)",
                    width=2,
                    dash="dash"
                ),
                fillcolor="rgba(0, 0, 0, 0)",
                layer="above"
            )

    # Ajouter une ligne de tendance
    fig.add_trace(
        go.Scatter(
            x=data["week"],
            y=data["volume"].rolling(window=3, min_periods=1).mean(),
            mode="lines",
            name=translate("trend", "charts"),
            line=dict(color="rgba(0, 0, 0, 0.7)", width=2, dash="dash"),
            hoverinfo="skip"
        )
    )

    # Mettre en évidence la semaine actuelle si spécifiée
    if current_week is not None and 0 <= current_week < len(weeks):
        current_volume = volumes[current_week]

        fig.add_trace(
            go.Scatter(
                # +1 car les semaines sont 1-based dans l'affichage
                x=[current_week + 1],
                y=[current_volume],
                mode="markers",
                marker=dict(
                    color="rgba(255, 255, 255, 1)",
                    size=12,
                    symbol="circle",
                    line=dict(color="rgba(0, 0, 0, 1)", width=2)
                ),
                name=translate("current_week", "charts"),
                hoverinfo="skip"
            )
        )

    # Configuration avancée
    fig.update_layout(
        xaxis=dict(
            tickmode="linear",
            tick0=1,
            dtick=1,
            title=dict(
                text=translate("week", "charts"),
                font=dict(size=14)
            ),
            gridcolor="rgba(0, 0, 0, 0.1)"
        ),
        yaxis=dict(
            title=dict(
                text=translate("volume_km", "charts"),
                font=dict(size=14)
            ),
            gridcolor="rgba(0, 0, 0, 0.1)"
        ),
        barmode="group",
        hovermode="closest",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        plot_bgcolor="white",
        margin=dict(l=60, r=30, t=80, b=60),
        height=400
    )

    # Personnaliser le hover
    fig.update_traces(
        hovertemplate=f"{translate('week', 'charts')} %{{x}}<br>{translate('volume', 'charts')}: %{{y:.1f}} km<extra></extra>"
    )

    # Afficher le graphique
    st.plotly_chart(fig, use_container_width=True, config={"responsive": True})


def render_intensity_distribution(
        plan: TrainingPlan,
        lang: str = "fr"
) -> None:
    """
    Affiche un graphique amélioré de la répartition des intensités d'entraînement

    Args:
        plan: Plan d'entraînement
        lang: Code de langue
    """
    # Calculer le temps passé à différentes intensités
    intensity_bins = {
        translate("recovery", "intensity"): 0,
        translate("easy", "intensity"): 0,
        translate("moderate", "intensity"): 0,
        translate("threshold", "intensity"): 0,
        translate("interval", "intensity"): 0,
        translate("race", "intensity"): 0
    }

    # Pour calculer aussi la distance à chaque intensité
    distance_bins = {k: 0 for k in intensity_bins.keys()}

    for session in plan.sessions.values():
        if session.session_type == SessionType.REST:
            continue

        for block in session.blocks:
            # Classer l'intensité en fonction de l'allure
            pace_seconds = block.pace.total_seconds()
            duration_mins = block.duration.total_seconds() / 60  # En minutes
            distance = block.distance

            if pace_seconds > 390:  # > 6:30/km
                intensity_bins[translate(
                    "recovery", "intensity")] += duration_mins
                distance_bins[translate("recovery", "intensity")] += distance
            elif pace_seconds > 330:  # 5:30-6:30/km
                intensity_bins[translate("easy", "intensity")] += duration_mins
                distance_bins[translate("easy", "intensity")] += distance
            elif pace_seconds > 270:  # 4:30-5:30/km
                intensity_bins[translate(
                    "moderate", "intensity")] += duration_mins
                distance_bins[translate("moderate", "intensity")] += distance
            elif pace_seconds > 240:  # 4:00-4:30/km
                intensity_bins[translate(
                    "threshold", "intensity")] += duration_mins
                distance_bins[translate("threshold", "intensity")] += distance
            elif pace_seconds > 210:  # 3:30-4:00/km
                intensity_bins[translate(
                    "interval", "intensity")] += duration_mins
                distance_bins[translate("interval", "intensity")] += distance
            else:  # < 3:30/km
                intensity_bins[translate("race", "intensity")] += duration_mins
                distance_bins[translate("race", "intensity")] += distance

    # Convertir en heures pour l'affichage et filtrer les valeurs nulles
    intensity_hours_dict = {
        zone: duration / 60  # Convertir minutes en heures
        for zone, duration in intensity_bins.items()
        if duration > 0
    }

    # Filtrer les zones de distance nulles
    distance_filtered = {
        zone: dist
        for zone, dist in distance_bins.items()
        if dist > 0
    }

    if not intensity_hours_dict:
        st.warning(translate("no_data_available", "charts"))
        return

    # Définir un ordre logique pour les intensités (du plus facile au plus difficile)
    intensity_order = [
        translate("recovery", "intensity"),
        translate("easy", "intensity"),
        translate("moderate", "intensity"),
        translate("threshold", "intensity"),
        translate("interval", "intensity"),
        translate("race", "intensity")
    ]

    # Filtrer et trier selon l'ordre défini
    ordered_intensities = [
        zone for zone in intensity_order if zone in intensity_hours_dict]
    ordered_hours = [intensity_hours_dict[zone]
                     for zone in ordered_intensities]
    ordered_distances = [distance_filtered.get(
        zone, 0) for zone in ordered_intensities]

    # Définir des couleurs pour chaque intensité
    intensity_colors = {
        translate("recovery", "intensity"): "rgba(158, 158, 158, 0.8)",  # Gris
        translate("easy", "intensity"): "rgba(33, 150, 243, 0.8)",       # Bleu
        translate("moderate", "intensity"): "rgba(76, 175, 80, 0.8)",    # Vert
        translate("threshold", "intensity"): "rgba(255, 193, 7, 0.8)",   # Jaune
        translate("interval", "intensity"): "rgba(255, 87, 34, 0.8)",    # Orange
        translate("race", "intensity"): "rgba(244, 67, 54, 0.8)"         # Rouge
    }

    colors = [intensity_colors.get(zone, "rgba(0, 0, 0, 0.7)")
              for zone in ordered_intensities]

    # Créer deux sous-graphiques pour le temps et la distance
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{"type": "bar"}, {"type": "pie"}]],
        subplot_titles=[
            translate("time_by_intensity", "charts"),
            translate("distance_by_intensity", "charts")
        ]
    )

    # Premier graphique: Temps par intensité (barres)
    fig.add_trace(
        go.Bar(
            x=ordered_intensities,
            y=ordered_hours,
            marker_color=colors,
            text=[f"{hours:.1f}h" for hours in ordered_hours],
            textposition="auto",
            hovertemplate="%{x}<br>%{y:.2f}h<extra></extra>"
        ),
        row=1, col=1
    )

    # Deuxième graphique: Distance par intensité (camembert)
    fig.add_trace(
        go.Pie(
            labels=ordered_intensities,
            values=ordered_distances,
            hole=0.4,
            textinfo="label+percent",
            hoverinfo="label+value+percent",
            hovertemplate="%{label}<br>%{value:.1f} km (%{percent})<extra></extra>",
            marker_colors=colors
        ),
        row=1, col=2
    )

    # Configuration avancée
    fig.update_layout(
        title=dict(
            text=translate("intensity_distribution", "charts"),
            font=dict(size=20)
        ),
        xaxis=dict(
            title=dict(
                text=translate("intensity_zone", "charts"),
                font=dict(size=14)
            ),
            categoryorder="array",
            categoryarray=ordered_intensities
        ),
        yaxis=dict(
            title=dict(
                text=translate("hours", "charts"),
                font=dict(size=14)
            )
        ),
        height=450,
        margin=dict(l=50, r=50, t=80, b=80),
        plot_bgcolor="white",
        paper_bgcolor="white",
        showlegend=False
    )

    # Rotation des labels sur l'axe X pour une meilleure lisibilité
    fig.update_xaxes(tickangle=45, row=1, col=1)

    # Afficher le graphique
    st.plotly_chart(fig, use_container_width=True, config={"responsive": True})


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
    # Compter les séances par type (en volume, pas en nombre)
    session_types_volume = {}
    session_types_count = {}

    for session in plan.sessions.values():
        if session.session_type != SessionType.REST:
            session_type = session.session_type.value
            translated_type = SESSION_TYPE_TRANSLATIONS.get(lang, {}).get(
                session_type, session_type
            )

            # Accumulation du volume
            session_types_volume[translated_type] = session_types_volume.get(
                translated_type, 0) + session.total_distance

            # Comptage des séances
            session_types_count[translated_type] = session_types_count.get(
                translated_type, 0) + 1

    if not session_types_volume:
        st.warning(translate("no_data_available", "charts"))
        return

    # Définir des couleurs cohérentes pour les types de séances
    session_type_colors = {
        SESSION_TYPE_TRANSLATIONS.get(lang, {}).get(SessionType.LONG_RUN.value, SessionType.LONG_RUN.value): "#43A047",
        SESSION_TYPE_TRANSLATIONS.get(lang, {}).get(SessionType.THRESHOLD.value, SessionType.THRESHOLD.value): "#E53935",
        SESSION_TYPE_TRANSLATIONS.get(lang, {}).get(SessionType.EF.value, SessionType.EF.value): "#039BE5",
        SESSION_TYPE_TRANSLATIONS.get(lang, {}).get(SessionType.RACE.value, SessionType.RACE.value): "#FDD835"
    }

    # Créer une figure à deux sous-graphiques
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{"type": "pie"}, {"type": "pie"}]],
        subplot_titles=[
            translate("volume_distribution", "charts"),
            translate("session_count_distribution", "charts")
        ]
    )

    # Premier graphique: Distribution du volume
    labels_volume = list(session_types_volume.keys())
    values_volume = list(session_types_volume.values())

    fig.add_trace(
        go.Pie(
            labels=labels_volume,
            values=values_volume,
            hole=0.4,
            textinfo="label+percent",
            hoverinfo="label+value+percent",
            hovertemplate="%{label}<br>%{value:.1f} km (%{percent})<extra></extra>",
            marker_colors=[session_type_colors.get(
                label, "#9E9E9E") for label in labels_volume]
        ),
        row=1, col=1
    )

    # Deuxième graphique: Distribution du nombre de séances
    labels_count = list(session_types_count.keys())
    values_count = list(session_types_count.values())

    fig.add_trace(
        go.Pie(
            labels=labels_count,
            values=values_count,
            hole=0.4,
            textinfo="label+percent",
            hoverinfo="label+value+percent",
            hovertemplate="%{label}<br>%{value} séances (%{percent})<extra></extra>",
            marker_colors=[session_type_colors.get(
                label, "#9E9E9E") for label in labels_count]
        ),
        row=1, col=2
    )

    # Mise en forme
    fig.update_layout(
        title=dict(
            text=translate("session_type_distribution", "charts"),
            font=dict(size=20)
        ),
        height=400,
        margin=dict(l=20, r=20, t=80, b=20),
        plot_bgcolor="white",
        paper_bgcolor="white",
        showlegend=False
    )

    # Afficher le graphique
    st.plotly_chart(fig, use_container_width=True, config={"responsive": True})


def render_phase_volume_distribution(
        plan: TrainingPlan,
        lang: str = "fr"
) -> None:
    """
    Affiche un graphique amélioré de la répartition du volume par phase

    Args:
        plan: Plan d'entraînement
        lang: Code de langue
    """
    # Calculer le volume par phase
    phase_stats = plan.get_phase_stats()

    if not phase_stats:
        st.warning(translate("no_data_available", "charts"))
        return

    # Préparer les données
    phases = []
    volumes = []
    colors = []
    num_weeks = []

    # Couleurs cohérentes pour les phases
    phase_colors = {
        TrainingPhase.DEVELOPMENT: "rgba(25, 118, 210, 0.7)",   # Bleu
        TrainingPhase.SPECIFIC: "rgba(56, 142, 60, 0.7)",       # Vert
        TrainingPhase.TAPER: "rgba(211, 47, 47, 0.7)"           # Rouge
    }

    for phase, stats in phase_stats.items():
        phase_name = PHASE_TRANSLATIONS.get(lang, {}).get(
            phase.value, phase.value
        )
        phases.append(phase_name)
        volumes.append(stats["total_volume"])
        colors.append(phase_colors.get(phase, "rgba(158, 158, 158, 0.7)"))
        num_weeks.append(stats["num_weeks"])

    # Créer le graphique
    fig = go.Figure()

    # Ajouter des barres avec un style amélioré
    fig.add_trace(go.Bar(
        x=phases,
        y=volumes,
        text=[f"{vol:.1f} km<br>{weeks} semaines" for vol,
              weeks in zip(volumes, num_weeks)],
        textposition="auto",
        marker_color=colors,
        hovertemplate="%{x}<br>Volume: %{y:.1f} km<br>Semaines: %{text}<extra></extra>"
    ))

    # Ajouter un indicateur du volume moyen hebdomadaire
    weekly_avg = [vol / weeks for vol, weeks in zip(volumes, num_weeks)]

    fig.add_trace(go.Scatter(
        x=phases,
        y=weekly_avg,
        mode="markers+text",
        marker=dict(
            color="rgba(255, 255, 255, 0.9)",
            size=10,
            symbol="circle",
            line=dict(color="rgba(0, 0, 0, 0.8)", width=2)
        ),
        text=[f"{avg:.1f} km/sem" for avg in weekly_avg],
        textposition="top center",
        name=translate("weekly_average", "charts"),
        hovertemplate="%{x}<br>Moyenne: %{y:.1f} km/semaine<extra></extra>"
    ))

    # Mise en forme du graphique
    fig.update_layout(
        title=dict(
            text=translate("volume_by_phase", "charts"),
            font=dict(size=20)
        ),
        xaxis=dict(
            title=dict(
                text=translate("phase", "charts"),
                font=dict(size=14)
            ),
            gridcolor="rgba(0, 0, 0, 0.05)"
        ),
        yaxis=dict(
            title=dict(
                text=translate("volume_km", "charts"),
                font=dict(size=14)
            ),
            gridcolor="rgba(0, 0, 0, 0.1)"
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=60, r=30, t=80, b=60),
        height=400,
        showlegend=False
    )

    # Afficher le graphique
    st.plotly_chart(fig, use_container_width=True, config={"responsive": True})


def render_training_load_chart(
        plan: TrainingPlan,
        lang: str = "fr",
        current_week: Optional[int] = None
) -> None:
    """
    Affiche un graphique amélioré de la charge d'entraînement

    Args:
        plan: Plan d'entraînement
        lang: Code de langue
        current_week: Numéro de la semaine actuelle (pour mise en évidence)
    """
    # Calculer la charge d'entraînement par semaine
    sessions_by_week = plan.get_sessions_by_week()

    weeks = sorted(sessions_by_week.keys())
    loads = []
    intensities = []
    volumes = []

    for week in weeks:
        week_sessions = sessions_by_week[week]

        # Somme des scores de difficulté pondérés par la distance
        total_distance = sum(s.total_distance for s in week_sessions
                             if s.session_type != SessionType.REST)
        volumes.append(total_distance)

        if total_distance > 0:
            # Calcul de l'intensité moyenne
            avg_intensity = sum(s.get_difficulty_score() * (s.total_distance / total_distance)
                                for s in week_sessions if s.total_distance > 0)
            intensities.append(avg_intensity)

            # Charge = intensité * volume (normalisée pour l'affichage)
            loads.append(avg_intensity * total_distance / 10)
        else:
            intensities.append(0)
            loads.append(0)

    # Convertir en numéros de semaine (1-based)
    week_numbers = [week + 1 for week in weeks]

    # Déterminer les phases pour chaque semaine
    phases = []
    for week in weeks:
        week_start, _ = plan.get_week_dates(week)
        phase = None
        for day in range(7):
            day_date = week_start + timedelta(days=day)
            day_phase = plan.get_phase_for_date(day_date)
            if day_phase:
                phase = day_phase
                break

        # Traduire le nom de la phase
        phase_name = translate(phase.value, "phases") if phase else "Unknown"
        phases.append(phase_name)

    # Créer le DataFrame
    data = pd.DataFrame({
        "week": week_numbers,
        "load": loads,
        "intensity": intensities,
        "volume": volumes,
        "phase": phases
    })

    # Créer un graphique à deux axes Y pour la charge et l'intensité
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Courbe de charge
    fig.add_trace(
        go.Scatter(
            x=data["week"],
            y=data["load"],
            mode="lines+markers",
            name=translate("training_load", "charts"),
            line=dict(color="rgba(33, 150, 243, 0.8)", width=3),
            marker=dict(size=8, color="rgba(33, 150, 243, 1)"),
            hovertemplate=f"{translate('week', 'charts')} %{{x}}<br>{translate('training_load', 'charts')}: %{{y:.1f}}<extra></extra>"
        ),
        secondary_y=False
    )

    # Courbe d'intensité
    fig.add_trace(
        go.Scatter(
            x=data["week"],
            y=data["intensity"],
            mode="lines+markers",
            name=translate("intensity", "charts"),
            line=dict(color="rgba(255, 87, 34, 0.8)", width=2, dash="dot"),
            marker=dict(size=6, color="rgba(255, 87, 34, 1)"),
            hovertemplate=f"{translate('week', 'charts')} %{{x}}<br>{translate('intensity', 'charts')}: %{{y:.2f}}<extra></extra>"
        ),
        secondary_y=True
    )

    # Mettre en évidence la semaine actuelle si spécifiée
    if current_week is not None and 0 <= current_week < len(weeks):
        current_load = loads[current_week]
        current_intensity = intensities[current_week]

        fig.add_trace(
            go.Scatter(
                # +1 car les semaines sont 1-based dans l'affichage
                x=[current_week + 1],
                y=[current_load],
                mode="markers",
                marker=dict(
                    color="rgba(255, 255, 255, 1)",
                    size=12,
                    symbol="circle",
                    line=dict(color="rgba(33, 150, 243, 1)", width=2)
                ),
                name=translate("current_week", "charts") +
                " (" + translate("load", "charts") + ")",
                hoverinfo="skip"
            ),
            secondary_y=False
        )

        fig.add_trace(
            go.Scatter(
                x=[current_week + 1],
                y=[current_intensity],
                mode="markers",
                marker=dict(
                    color="rgba(255, 255, 255, 1)",
                    size=10,
                    symbol="circle",
                    line=dict(color="rgba(255, 87, 34, 1)", width=2)
                ),
                name=translate("current_week", "charts") +
                " (" + translate("intensity", "charts") + ")",
                hoverinfo="skip"
            ),
            secondary_y=True
        )

    # Ajouter des annotations pour les phases
    phase_changes = []
    current_phase = None

    for i, phase in enumerate(phases):
        if phase != current_phase:
            phase_changes.append((i, phase))
            current_phase = phase

    for i, (week_idx, phase) in enumerate(phase_changes):
        # Définir les couleurs selon la phase
        colors = {
            translate(TrainingPhase.DEVELOPMENT.value, "phases"): "rgba(25, 118, 210, 1)",
            translate(TrainingPhase.SPECIFIC.value, "phases"): "rgba(56, 142, 60, 1)",
            translate(TrainingPhase.TAPER.value, "phases"): "rgba(211, 47, 47, 1)"
        }

        color = colors.get(phase, "rgba(0, 0, 0, 0.7)")

        # Ne pas afficher l'annotation pour la première semaine (début du plan)
        if i > 0:
            fig.add_vline(
                x=week_numbers[week_idx],
                line_width=1,
                line_dash="dash",
                line_color=color,
                annotation_text=phase,
                annotation_position="top"
            )

    # Mise en forme du graphique
    fig.update_layout(
        title=dict(
            text=translate("training_load_evolution", "charts"),
            font=dict(size=20)
        ),
        xaxis=dict(
            title=dict(
                text=translate("week", "charts"),
                font=dict(size=14)
            ),
            gridcolor="rgba(0, 0, 0, 0.1)"
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=60, r=60, t=80, b=60),
        height=450,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hovermode="x unified"
    )

    # Configurer les axes Y
    fig.update_yaxes(
        title_text=translate("training_load", "charts"),
        gridcolor="rgba(0, 0, 0, 0.1)",
        secondary_y=False
    )

    fig.update_yaxes(
        title_text=translate("intensity_factor", "charts"),
        gridcolor="rgba(0, 0, 0, 0)",
        secondary_y=True,
        range=[0, max(intensities) * 1.1]  # Ajuster l'échelle pour l'intensité
    )

    # Afficher le graphique
    st.plotly_chart(fig, use_container_width=True, config={"responsive": True})


def render_weekly_distance_by_type(
        plan: TrainingPlan,
        week_num: int,
        lang: str = "fr"
) -> None:
    """
    Affiche un graphique amélioré de la répartition du volume par type de séance pour une semaine

    Args:
        plan: Plan d'entraînement
        week_num: Numéro de la semaine
        lang: Code de langue
    """
    # Récupérer les séances de la semaine
    sessions_by_week = plan.get_sessions_by_week()

    if week_num not in sessions_by_week:
        st.warning(translate("no_data_available", "charts"))
        return

    # Calculer la distance par type et jour de séance
    session_types_data = []

    # Créer un dictionnaire de couleurs cohérentes
    session_type_colors = {
        SessionType.LONG_RUN: "#43A047",  # Vert
        SessionType.THRESHOLD: "#E53935",  # Rouge
        SessionType.EF: "#039BE5",        # Bleu
        SessionType.RACE: "#FDD835"       # Jaune
    }

    for session in sessions_by_week[week_num]:
        if session.session_type == SessionType.REST:
            continue

        # Traduire le type de séance
        type_name = SESSION_TYPE_TRANSLATIONS.get(lang, {}).get(
            session.session_type.value,
            session.session_type.value
        )

        # Traduire le jour de la semaine
        day_name = translate(f"day_{session.session_date.weekday()}",
                             "common") or f"Jour {session.session_date.weekday() + 1}"

        # Déterminer la couleur
        color = session_type_colors.get(session.session_type, "#9E9E9E")

        session_types_data.append({
            "type": type_name,
            "day": day_name,
            "day_num": session.session_date.weekday(),
            "distance": session.total_distance,
            "duration": session.total_duration.total_seconds() / 60,  # En minutes
            "color": color
        })

    if not session_types_data:
        st.warning(translate("no_sessions_this_week", "charts"))
        return

    # Créer un DataFrame
    df = pd.DataFrame(session_types_data)

    # Trier par jour de semaine
    df = df.sort_values(by="day_num")

    # Créer deux sous-graphiques: répartition par type et par jour
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{"type": "pie"}, {"type": "bar"}]],
        subplot_titles=[
            translate("volume_by_type", "charts"),
            translate("volume_by_day", "charts")
        ]
    )

    # Premier graphique: Volume par type de séance
    by_type = df.groupby("type").sum().reset_index()

    fig.add_trace(
        go.Pie(
            labels=by_type["type"],
            values=by_type["distance"],
            hole=0.4,
            textinfo="label+percent",
            hoverinfo="label+value+percent",
            hovertemplate="%{label}<br>%{value:.1f} km (%{percent})<extra></extra>",
            marker_colors=df.groupby("type")["color"].first().values
        ),
        row=1, col=1
    )

    # Deuxième graphique: Volume par jour
    fig.add_trace(
        go.Bar(
            x=df["day"],
            y=df["distance"],
            marker_color=df["color"],
            text=df["type"],
            hovertemplate="%{x}<br>%{y:.1f} km<br>%{text}<extra></extra>"
        ),
        row=1, col=2
    )

    # Configuration avancée
    fig.update_layout(
        title=dict(
            text=translate("weekly_volume_distribution", "charts"),
            font=dict(size=20)
        ),
        height=400,
        margin=dict(l=50, r=50, t=80, b=50),
        plot_bgcolor="white",
        paper_bgcolor="white",
        showlegend=False
    )

    # Personnalisation de l'axe X et Y du graphique à barres
    fig.update_xaxes(title_text=translate("day", "charts"), row=1, col=2)
    fig.update_yaxes(title_text=translate(
        "distance_km", "charts"), row=1, col=2)

    # Afficher le graphique
    st.plotly_chart(fig, use_container_width=True, config={"responsive": True})


def render_comparison_chart(
        original_plan: TrainingPlan,
        simulated_plan: TrainingPlan,
        metric: str = "volume",  # volume, intensity, sessions
        lang: str = "fr"
) -> None:
    """
    Affiche un graphique amélioré comparant deux plans d'entraînement

    Args:
        original_plan: Plan d'entraînement original
        simulated_plan: Plan d'entraînement simulé
        metric: Métrique à comparer (volume, intensity, sessions)
        lang: Code de langue
    """
    if metric == "volume":
        # Comparer les volumes hebdomadaires
        original_weeks = sorted(original_plan.weekly_volumes.keys())
        original_volumes = [original_plan.weekly_volumes[week]
                            for week in original_weeks]
        original_week_numbers = [week + 1 for week in original_weeks]

        simulated_weeks = sorted(simulated_plan.weekly_volumes.keys())
        simulated_volumes = [simulated_plan.weekly_volumes[week]
                             for week in simulated_weeks]
        simulated_week_numbers = [week + 1 for week in simulated_weeks]

        # Déterminer le nombre maximum de semaines pour l'axe X
        max_week = max(
            max(original_week_numbers) if original_week_numbers else 0,
            max(simulated_week_numbers) if simulated_week_numbers else 0
        )

        # Créer la figure
        fig = go.Figure()

        # Ajouter les traces pour chaque plan
        fig.add_trace(
            go.Bar(
                x=original_week_numbers,
                y=original_volumes,
                name=translate("original", "charts"),
                marker_color="rgba(33, 150, 243, 0.7)",
                hovertemplate=f"{translate('week', 'charts')} %{{x}}<br>{translate('volume', 'charts')}: %{{y:.1f}} km<extra></extra>"
            )
        )

        fig.add_trace(
            go.Bar(
                x=simulated_week_numbers,
                y=simulated_volumes,
                name=translate("simulated", "charts"),
                marker_color="rgba(76, 175, 80, 0.7)",
                hovertemplate=f"{translate('week', 'charts')} %{{x}}<br>{translate('volume', 'charts')}: %{{y:.1f}} km<extra></extra>"
            )
        )

        # Ajouter les lignes de tendance
        fig.add_trace(
            go.Scatter(
                x=original_week_numbers,
                y=pd.Series(original_volumes).rolling(
                    window=3, min_periods=1).mean(),
                mode="lines",
                name=translate("original_trend", "charts"),
                line=dict(color="rgba(33, 150, 243, 1)", width=2, dash="dash"),
                hoverinfo="skip"
            )
        )

        fig.add_trace(
            go.Scatter(
                x=simulated_week_numbers,
                y=pd.Series(simulated_volumes).rolling(
                    window=3, min_periods=1).mean(),
                mode="lines",
                name=translate("simulated_trend", "charts"),
                line=dict(color="rgba(76, 175, 80, 1)", width=2, dash="dash"),
                hoverinfo="skip"
            )
        )

        # Configuration avancée
        fig.update_layout(
            title=dict(
                text=translate("volume_comparison", "charts"),
                font=dict(size=20)
            ),
            xaxis=dict(
                title=dict(
                    text=translate("week", "charts"),
                    font=dict(size=14)
                ),
                tickmode="linear",
                tick0=1,
                dtick=1,
                range=[0.5, max_week + 0.5],
                gridcolor="rgba(0, 0, 0, 0.1)"
            ),
            yaxis=dict(
                title=dict(
                    text=translate("volume_km", "charts"),
                    font=dict(size=14)
                ),
                gridcolor="rgba(0, 0, 0, 0.1)"
            ),
            barmode="group",
            bargap=0.15,
            bargroupgap=0.1,
            plot_bgcolor="white",
            paper_bgcolor="white",
            margin=dict(l=50, r=30, t=80, b=50),
            height=500,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

    elif metric == "intensity":
        # Comparer l'intensité (calculer un score moyen par semaine)
        original_intensity = []
        simulated_intensity = []
        weeks = []

        max_week = max(
            max(original_plan.weekly_volumes.keys()
                ) if original_plan.weekly_volumes else 0,
            max(simulated_plan.weekly_volumes.keys()
                ) if simulated_plan.weekly_volumes else 0
        )

        for week in range(max_week + 1):
            # Séances du plan original
            original_sessions = [s for s in original_plan.sessions.values()
                                 if (s.session_date - original_plan.user_data.start_date).days // 7 == week]

            # Séances du plan simulé
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
                original_intensity.append(None)

            if simulated_total_distance > 0:
                simulated_score = sum(s.get_difficulty_score() * (s.total_distance / simulated_total_distance)
                                      for s in simulated_sessions if s.total_distance > 0)
                simulated_intensity.append(simulated_score)
            else:
                simulated_intensity.append(None)

            weeks.append(week + 1)  # 1-based

        # Créer la figure
        fig = go.Figure()

        # Ajouter les traces pour chaque plan
        fig.add_trace(
            go.Scatter(
                x=weeks,
                y=original_intensity,
                mode="lines+markers",
                name=translate("original", "charts"),
                line=dict(color="rgba(33, 150, 243, 0.8)", width=3),
                marker=dict(size=8, color="rgba(33, 150, 243, 1)"),
                hovertemplate=f"{translate('week', 'charts')} %{{x}}<br>{translate('intensity', 'charts')}: %{{y:.2f}}<extra></extra>"
            )
        )

        fig.add_trace(
            go.Scatter(
                x=weeks,
                y=simulated_intensity,
                mode="lines+markers",
                name=translate("simulated", "charts"),
                line=dict(color="rgba(76, 175, 80, 0.8)", width=3),
                marker=dict(size=8, color="rgba(76, 175, 80, 1)"),
                hovertemplate=f"{translate('week', 'charts')} %{{x}}<br>{translate('intensity', 'charts')}: %{{y:.2f}}<extra></extra>"
            )
        )

        # Configuration avancée
        fig.update_layout(
            title=dict(
                text=translate("intensity_comparison", "charts"),
                font=dict(size=20)
            ),
            xaxis=dict(
                title=dict(
                    text=translate("week", "charts"),
                    font=dict(size=14)
                ),
                tickmode="linear",
                tick0=1,
                dtick=1,
                gridcolor="rgba(0, 0, 0, 0.1)"
            ),
            yaxis=dict(
                title=dict(
                    text=translate("intensity_score", "charts"),
                    font=dict(size=14)
                ),
                gridcolor="rgba(0, 0, 0, 0.1)"
            ),
            plot_bgcolor="white",
            paper_bgcolor="white",
            margin=dict(l=50, r=30, t=80, b=50),
            height=500,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

    else:  # sessions
        # Comparer le nombre de séances par type
        original_types = {}
        original_volume_by_type = {}

        for session in original_plan.sessions.values():
            if session.session_type != SessionType.REST:
                session_type = session.session_type.value
                translated_type = SESSION_TYPE_TRANSLATIONS.get(lang, {}).get(
                    session_type, session_type
                )

                # Comptage des séances
                original_types[translated_type] = original_types.get(
                    translated_type, 0) + 1

                # Calcul du volume par type
                original_volume_by_type[translated_type] = original_volume_by_type.get(
                    translated_type, 0) + session.total_distance

        simulated_types = {}
        simulated_volume_by_type = {}

        for session in simulated_plan.sessions.values():
            if session.session_type != SessionType.REST:
                session_type = session.session_type.value
                translated_type = SESSION_TYPE_TRANSLATIONS.get(lang, {}).get(
                    session_type, session_type
                )

                # Comptage des séances
                simulated_types[translated_type] = simulated_types.get(
                    translated_type, 0) + 1

                # Calcul du volume par type
                simulated_volume_by_type[translated_type] = simulated_volume_by_type.get(
                    translated_type, 0) + session.total_distance

        # Combiner les types pour avoir le même ensemble dans les deux plans
        all_types = sorted(set(original_types.keys()) |
                           set(simulated_types.keys()))

        # Créer deux sous-graphiques pour le nombre de séances et le volume par type
        fig = make_subplots(
            rows=1, cols=2,
            specs=[[{"type": "bar"}, {"type": "bar"}]],
            subplot_titles=[
                translate("session_count_comparison", "charts"),
                translate("volume_by_type_comparison", "charts")
            ]
        )

        # Premier graphique: Nombre de séances par type
        fig.add_trace(
            go.Bar(
                name=translate("original", "charts"),
                x=all_types,
                y=[original_types.get(t, 0) for t in all_types],
                marker_color="rgba(33, 150, 243, 0.7)",
                hovertemplate="%{x}<br>%{y} séances<extra></extra>"
            ),
            row=1, col=1
        )

        fig.add_trace(
            go.Bar(
                name=translate("simulated", "charts"),
                x=all_types,
                y=[simulated_types.get(t, 0) for t in all_types],
                marker_color="rgba(76, 175, 80, 0.7)",
                hovertemplate="%{x}<br>%{y} séances<extra></extra>"
            ),
            row=1, col=1
        )

        # Deuxième graphique: Volume par type
        fig.add_trace(
            go.Bar(
                name=translate("original", "charts"),
                x=all_types,
                y=[original_volume_by_type.get(t, 0) for t in all_types],
                marker_color="rgba(33, 150, 243, 0.7)",
                hovertemplate="%{x}<br>%{y:.1f} km<extra></extra>"
            ),
            row=1, col=2
        )

        fig.add_trace(
            go.Bar(
                name=translate("simulated", "charts"),
                x=all_types,
                y=[simulated_volume_by_type.get(t, 0) for t in all_types],
                marker_color="rgba(76, 175, 80, 0.7)",
                hovertemplate="%{x}<br>%{y:.1f} km<extra></extra>"
            ),
            row=1, col=2
        )

        # Configuration avancée
        fig.update_layout(
            title=dict(
                text=translate("session_comparison", "charts"),
                font=dict(size=20)
            ),
            barmode="group",
            height=500,
            plot_bgcolor="white",
            paper_bgcolor="white",
            margin=dict(l=50, r=30, t=100, b=80),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        # Configuration des axes
        fig.update_xaxes(
            title_text=translate("session_type", "charts"),
            tickangle=45,
            row=1, col=1
        )

        fig.update_xaxes(
            title_text=translate("session_type", "charts"),
            tickangle=45,
            row=1, col=2
        )

        fig.update_yaxes(
            title_text=translate("count", "charts"),
            gridcolor="rgba(0, 0, 0, 0.1)",
            row=1, col=1
        )

        fig.update_yaxes(
            title_text=translate("volume_km", "charts"),
            gridcolor="rgba(0, 0, 0, 0.1)",
            row=1, col=2
        )

    # Afficher le graphique
    st.plotly_chart(fig, use_container_width=True, config={"responsive": True})
