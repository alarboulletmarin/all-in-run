"""
Package components - Composants d'interface utilisateur réutilisables pour l'application All-in-Run.
"""
from .forms import (
    render_date_selector,
    render_pace_input,
    render_time_input,
    render_race_type_selector,
    render_sessions_per_week_selector,
    render_volume_inputs,
    render_intermediate_race_form,
    create_paces_summary
)

from .calendar import (
    render_week_navigation,
    render_weekly_summary,
    render_week_calendar,
    render_session_card,
    render_month_calendar,
    render_session_details,
    render_phase_timeline
)

from .charts import (
    render_volume_chart,
    render_session_type_distribution,
    render_phase_volume_distribution,
    render_training_load_chart,
    render_weekly_distance_by_type,
    render_intensity_distribution,
    render_comparison_chart
)

__all__ = [
    # Forms
    'render_date_selector',
    'render_pace_input',
    'render_time_input',
    'render_race_type_selector',
    'render_sessions_per_week_selector',
    'render_volume_inputs',
    'render_intermediate_race_form',
    'create_paces_summary',

    # Calendar
    'render_week_navigation',
    'render_weekly_summary',
    'render_week_calendar',
    'render_session_card',
    'render_month_calendar',
    'render_session_details',
    'render_phase_timeline',

    # Charts
    'render_volume_chart',
    'render_session_type_distribution',
    'render_phase_volume_distribution',
    'render_training_load_chart',
    'render_weekly_distance_by_type',
    'render_intensity_distribution',
    'render_comparison_chart'
]