"""
Page d'affichage du plan d'entraînement.
"""
import streamlit as st
from datetime import date, timedelta
import io
import base64
from typing import Dict, List, Any, Optional
import pandas as pd

from controllers.plan_controller import PlanController
from models.plan import TrainingPlan
from models.session import Session, SessionType, TrainingPhase
from utils.date_utils import format_date, get_week_number
from utils.time_converter import format_timedelta, format_pace
from utils.i18n import _
from ui.components import (
    render_week_navigation,
    render_weekly_summary,
    render_week_calendar,
    render_session_details,
    render_phase_timeline,
    render_volume_chart,
    render_session_type_distribution,
    render_phase_volume_distribution,
    render_training_load_chart
)


def handle_export_ics(plan_controller: PlanController):
    """
    Gestionnaire pour l'export ICS

    Args:
        plan_controller: Contrôleur du plan d'entraînement
    """
    ics_data = plan_controller.export_to_ics()

    if ics_data:
        # Créer un lien de téléchargement
        b64 = base64.b64encode(ics_data).decode()
        href = f'<a href="data:text/calendar;charset=utf-8;base64,{b64}" download="training_plan.ics">{_("download_ics", "plan_page")}</a>'
        st.markdown(href, unsafe_allow_html=True)

def handle_export_tcx(plan_controller: PlanController):
    """
    Gestionnaire pour l'export TCX pour Garmin

    Args:
        plan_controller: Contrôleur du plan d'entraînement
    """
    tcx_data = plan_controller.export_to_tcx()

    if tcx_data:
        # Créer un lien de téléchargement
        b64 = base64.b64encode(tcx_data).decode()
        href = f'<a href="data:application/tcx+xml;base64,{b64}" download="training_plan_garmin.tcx">{_("download_tcx", "plan_page")}</a>'
        st.markdown(href, unsafe_allow_html=True)

def handle_export_pdf(plan_controller: PlanController):
    """
    Gestionnaire pour l'export PDF

    Args:
        plan_controller: Contrôleur du plan d'entraînement
    """
    pdf_data = plan_controller.export_to_pdf()

    if pdf_data:
        # Créer un lien de téléchargement
        b64 = base64.b64encode(pdf_data).decode()
        href = f'<a href="data:application/pdf;base64,{b64}" download="training_plan.pdf">{_("download_pdf", "plan_page")}</a>'
        st.markdown(href, unsafe_allow_html=True)


def handle_export_json(plan_controller: PlanController):
    """
    Gestionnaire pour l'export JSON

    Args:
        plan_controller: Contrôleur du plan d'entraînement
    """
    json_data = plan_controller.export_to_json()

    if json_data:
        # Créer un lien de téléchargement
        b64 = base64.b64encode(json_data.encode()).decode()
        href = f'<a href="data:application/json;base64,{b64}" download="training_plan.json">{_("download_json", "plan_page")}</a>'
        st.markdown(href, unsafe_allow_html=True)


def handle_import_json(plan_controller: PlanController, file_data):
    """
    Gestionnaire pour l'import JSON

    Args:
        plan_controller: Contrôleur du plan d'entraînement
        file_data: Données du fichier JSON
    """
    try:
        json_str = io.StringIO(file_data.getvalue().decode("utf-8")).read()
        imported_plan = plan_controller.import_from_json(json_str)

        if imported_plan:
            st.session_state["current_plan"] = imported_plan
            st.success(_("import_success", "plan_page"))

            # Passer à l'affichage du plan
            st.session_state["view_mode"] = "calendar"
            st.rerun()
        else:
            st.error(_("import_error", "plan_page"))

    except Exception as e:
        st.error(f"{_('import_error', 'plan_page')}: {str(e)}")


def handle_adjust_plan(plan_controller: PlanController):
    """
    Gestionnaire pour l'ajustement du plan à la date courante

    Args:
        plan_controller: Contrôleur du plan d'entraînement
    """
    adjusted_plan = plan_controller.adjust_to_current_date()

    if adjusted_plan:
        st.session_state["current_plan"] = adjusted_plan
        st.success(_("adjust_success", "plan_page"))
        st.rerun()
    else:
        st.error(_("adjust_error", "plan_page"))


def handle_week_change(week_num: int):
    """
    Gestionnaire pour le changement de semaine

    Args:
        week_num: Numéro de la semaine à afficher
    """
    st.session_state["current_week"] = week_num


def handle_session_click(session_date: date):
    """
    Gestionnaire pour le clic sur une séance

    Args:
        session_date: Date de la séance
    """
    st.session_state["selected_session_date"] = session_date


def generate_plan(plan_controller: PlanController):
    """
    Génère le plan d'entraînement

    Args:
        plan_controller: Contrôleur du plan d'entraînement
    """
    # Vérifier si les données utilisateur sont présentes
    if "user_data" not in st.session_state:
        st.error(_("no_user_data", "plan_page"))

        # Bouton pour retourner à la page d'entrée
        if st.button(_("back_to_input", "plan_page")):
            st.session_state["page"] = "input"
            st.rerun()

        return

    with st.spinner(_("generating_plan", "plan_page")):
        try:
            # Générer le plan
            plan = plan_controller.generate_plan(st.session_state["user_data"])

            if plan:
                # Afficher un message à l'utilisateur
                st.success(_("plan_generated", "plan_page"))

                # Stocker le plan dans la session
                st.session_state["current_plan"] = plan

                # Initialiser la semaine courante
                if "current_week" not in st.session_state:
                    st.session_state["current_week"] = 0

                # Initialiser le mode d'affichage
                if "view_mode" not in st.session_state:
                    st.session_state["view_mode"] = "calendar"

                # Pour le débogage
                st.write("Plan généré et stocké dans session_state")
                return plan
            else:
                st.error(_("plan_generation_error", "plan_page"))
                return None
        except Exception as e:
            st.error(f"Erreur durant la génération du plan: {str(e)}")
            return None

def render_plan_summary(plan: TrainingPlan):
    """
    Affiche un résumé du plan d'entraînement

    Args:
        plan: Plan d'entraînement
    """
    st.header(_("plan_summary", "plan_page"))

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"**{_('start_date', 'plan_page')}:** {format_date(plan.user_data.start_date)}")
        st.markdown(f"**{_('race_date', 'plan_page')}:** {format_date(plan.user_data.main_race.race_date)}")
        st.markdown(f"**{_('race_type', 'plan_page')}:** {_(plan.user_data.main_race.race_type.value, 'race_types')}")

    with col2:
        st.markdown(f"**{_('total_weeks', 'plan_page')}:** {plan.user_data.total_weeks}")
        st.markdown(f"**{_('sessions_per_week', 'plan_page')}:** {plan.user_data.sessions_per_week}")
        st.markdown(f"**{_('total_sessions', 'plan_page')}:** {len([s for s in plan.sessions.values() if s.session_type != SessionType.REST])}")

    with col3:
        st.markdown(f"**{_('total_volume', 'plan_page')}:** {plan.get_total_volume()} km")
        st.markdown(f"**{_('total_duration', 'plan_page')}:** {format_timedelta(plan.get_total_duration(), 'hms_text')}")

        # Calculer le nombre de séances par type
        session_counts = {}
        for session in plan.sessions.values():
            if session.session_type != SessionType.REST:
                session_type = session.session_type.value
                session_counts[session_type] = session_counts.get(session_type, 0) + 1

        # Afficher le nombre de séances par type (limité aux principaux)
        for session_type in [SessionType.LONG_RUN.value, SessionType.THRESHOLD.value]:
            if session_type in session_counts:
                st.markdown(f"**{_(session_type, 'session_types')}:** {session_counts[session_type]}")


def render_export_import_section(plan_controller: PlanController):
    """
    Affiche la section d'export/import du plan
    """
    st.header(_("export_import", "plan_page"))

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        # Export ICS
        if st.button(_("export_ics", "plan_page")):
            handle_export_ics(plan_controller)

    with col2:
        # Export PDF
        if st.button(_("export_pdf", "plan_page")):
            handle_export_pdf(plan_controller)

    with col3:
        # Export JSON
        if st.button(_("export_json", "plan_page")):
            handle_export_json(plan_controller)

    with col4:
        # Export TCX (pour Garmin)
        if st.button(_("export_tcx", "plan_page")):
            handle_export_tcx(plan_controller)

    # Import JSON
    st.subheader(_("import_plan", "plan_page"))

    uploaded_file = st.file_uploader(
        _("upload_json", "plan_page"),
        type=["json"],
        help=_("import_help", "plan_page")
    )

    if uploaded_file is not None:
        handle_import_json(plan_controller, uploaded_file)

    # Ajustement du plan
    st.subheader(_("adjust_plan", "plan_page"))

    if st.button(_("adjust_to_current_date", "plan_page")):
        handle_adjust_plan(plan_controller)


def render_week_view(plan: TrainingPlan, current_week: int):
    """
    Affiche la vue hebdomadaire du plan

    Args:
        plan: Plan d'entraînement
        current_week: Numéro de la semaine à afficher
    """
    # Navigation entre les semaines
    render_week_navigation(plan, current_week, handle_week_change)

    # Résumé de la semaine
    render_weekly_summary(plan, current_week)

    # Calendrier de la semaine
    render_week_calendar(plan, current_week, on_session_click=handle_session_click)

    # Détails de la séance si une séance est sélectionnée
    if "selected_session_date" in st.session_state:
        session_date = st.session_state["selected_session_date"]
        session = plan.get_session(session_date)

        if session:
            st.divider()
            render_session_details(session)


def render_statistics_view(plan: TrainingPlan):
    """
    Affiche la vue statistique du plan

    Args:
        plan: Plan d'entraînement
    """
    st.header(_("plan_statistics", "plan_page"))

    # Timeline des phases
    render_phase_timeline(plan)

    # Graphiques
    col1, col2 = st.columns(2)

    with col1:
        render_volume_chart(plan, current_week=st.session_state.get("current_week"))
        render_phase_volume_distribution(plan)

    with col2:
        render_session_type_distribution(plan)
        render_training_load_chart(plan, current_week=st.session_state.get("current_week"))


def render_export_view(plan: TrainingPlan):
    """
    Affiche la vue export du plan

    Args:
        plan: Plan d'entraînement
    """
    st.header(_("export_view", "plan_page"))

    # Générer un DataFrame pour l'affichage tabulaire
    data = []

    for session_date, session in sorted(plan.sessions.items()):
        if session.session_type == SessionType.REST:
            continue

        # Calculer le numéro de semaine
        week_num = get_week_number(session_date, plan.user_data.start_date) + 1  # 1-indexed

        # Créer une ligne pour le DataFrame
        row = {
            _("week", "plan_page"): week_num,
            _("date", "plan_page"): format_date(session_date),
            _("type", "plan_page"): _(session.session_type.value, "session_types"),
            _("phase", "plan_page"): _(session.phase.value, "phases"),
            _("distance", "plan_page"): f"{session.total_distance} km",
            _("duration", "plan_page"): format_timedelta(session.total_duration, "hms_text"),
            _("description", "plan_page"): session.description
        }

        data.append(row)

    # Créer le DataFrame
    df = pd.DataFrame(data)

    # Afficher le tableau complet
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    # Option pour télécharger en CSV
    if data:
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label=_("download_csv", "plan_page"),
            data=csv,
            file_name="training_plan.csv",
            mime="text/csv"
        )


def render_plan_view_page(plan_controller: PlanController):
    """
    Affiche la page de visualisation du plan d'entraînement

    Args:
        plan_controller: Contrôleur du plan d'entraînement
    """
    st.title(_("plan_view_title", "plan_page"))

    # Vérifier si un plan existe ou doit être généré
    current_plan = st.session_state.get("current_plan")

    if current_plan is None:
        current_plan = plan_controller.get_current_plan()

    if current_plan is None:
        # Générer le plan si les données utilisateur sont présentes
        current_plan = generate_plan(plan_controller)

        if current_plan is None:
            # Si aucun plan n'a pu être généré, on s'arrête ici
            return

    # À partir d'ici, on a un plan valide à afficher
    # Afficher un résumé du plan
    render_plan_summary(current_plan)

    # Tabs pour les différentes vues
    tab1, tab2, tab3, tab4 = st.tabs([
        _("calendar", "plan_page"),
        _("statistics", "plan_page"),
        _("export", "plan_page"),
        _("export_import", "plan_page")
    ])

    with tab1:
        # Vue calendrier
        render_week_view(current_plan, st.session_state.get("current_week", 0))

    with tab2:
        # Vue statistique
        render_statistics_view(current_plan)

    with tab3:
        # Vue export (tableau)
        render_export_view(current_plan)

    with tab4:
        # Boutons d'export et import
        render_export_import_section(plan_controller)

    # Bouton pour revenir à la page d'entrée
    st.divider()

    if st.button(_("back_to_input", "plan_page")):
        st.session_state["page"] = "input"
        st.rerun()