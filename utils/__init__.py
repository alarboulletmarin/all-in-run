"""
Package utils - Utilitaires pour l'application All-in-Run.
"""
from .date_utils import *
from .time_converter import *
from .pace_calculator import *
from .validators import *
from .storage import storage_manager
from .i18n import i18n, _

__all__ = [
    # Classes et fonctions exportées de date_utils.py
    'get_next_monday',
    'get_sunday',
    'get_first_day_of_week',
    'get_days_between',
    'get_weeks_between',
    'get_week_number',
    'get_date_from_week_and_day',
    'format_date',
    'get_date_range_for_month',
    'days_between',
    'weeks_between',
    'yield_month_calendar',

    # Classes et fonctions exportées de time_converter.py
    'parse_time_string',
    'format_timedelta',
    'format_pace',
    'parse_pace_string',
    'calculate_time_from_distance_and_pace',
    'calculate_pace_from_distance_and_time',
    'add_time_to_pace',
    'format_duration_for_calendar',

    # Classes et fonctions exportées de pace_calculator.py
    'calculate_ef_pace',
    'calculate_specific_ef_pace',
    'calculate_race_pace',
    'estimate_race_time',
    'estimate_race_pace',
    'get_equivalent_paces',
    'get_vdot_from_pace',
    'get_training_paces_from_vdot',

    # Classes et fonctions exportées de validators.py
    'validate_date_range',
    'validate_course_info',
    'validate_paces',
    'validate_volume',
    'validate_sessions_per_week',
    'validate_intermediate_races',
    'validate_user_input',

    # Classes et fonctions exportées de storage.py
    'storage_manager',

    # Classes et fonctions exportées de i18n.py
    'i18n',
    '_'
]