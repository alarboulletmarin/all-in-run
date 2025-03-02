"""
Package ui - Interface utilisateur pour l'application All-in-Run.
"""
from .pages import render_input_form, render_plan_view_page, render_simulation_page
from .components import (
    # Forms
    render_date_selector,
    render_pace_input,
    render_time_input,
    render_race_type_selector,
    render_sessions_per_week_selector,
    render_volume_inputs,
    render_intermediate_race_form,
    create_paces_summary,

    # Calendar
    render_week_navigation,
    render_weekly_summary,
    render_week_calendar,
    render_session_card,
    render_session_details,
    render_phase_timeline,

    # Charts
    render_volume_chart,
    render_session_type_distribution,
    render_phase_volume_distribution,
    render_training_load_chart,
    render_weekly_distance_by_type,
    render_intensity_distribution,
    render_comparison_chart
)

__all__ = [
    'render_input_form',
    'render_plan_view_page',
    'render_simulation_page',

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