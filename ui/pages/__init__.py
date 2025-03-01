"""
Package pages - Pages de l'interface utilisateur pour l'application All-in-Run.
"""
from .input_page import render_input_form
from .plan_view_page import render_plan_view_page
from .simulation_page import render_simulation_page

__all__ = [
    'render_input_form',
    'render_plan_view_page',
    'render_simulation_page'
]