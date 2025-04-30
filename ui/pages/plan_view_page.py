import base64
import hashlib
import io
import json
from datetime import date

import streamlit as st

from controllers.plan_controller import PlanController
from models.plan import TrainingPlan
from models.session import SessionType
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
from utils.date_utils import format_date
from utils.i18n import _ as translate
from utils.time_converter import format_timedelta


def handle_export_ics(plan_controller: PlanController):
    """
    Gestionnaire pour l'export ICS

    Args:
        plan_controller: Contrôleur du plan d'entraînement
    """
    # Options par défaut simples pour l'export simple
    options = {
        "include_rest_days": False,
        "reminder_time": 30,
        "start_time": 18,
        "ics_calendar_name": "All-in-Run Plan"
    }

    ics_data = plan_controller.export_to_ics(options=options)

    if ics_data:
        # Créer un lien de téléchargement
        b64 = base64.b64encode(ics_data).decode()
        filename = f"plan_entrainement_{options['ics_calendar_name'].replace(' ', '_')}.ics"
        href = f'<a href="data:text/calendar;charset=utf-8;base64,{b64}" download="{filename}" class="download-link" target="_blank">{translate("download_ics", "plan_page")}</a>'

        st.success(translate("ics_export_success", "plan_page"))
        st.markdown(href, unsafe_allow_html=True)

        with st.expander(translate("ics_import_instructions", "plan_page")):
            st.markdown(translate("ics_import_steps", "plan_page"))
            st.markdown("""
            ### Instructions spécifiques pour iPhone :
            1. Téléchargez le fichier ICS
            2. Appuyez sur le fichier téléchargé
            3. Sélectionnez "Ouvrir dans Calendrier"
            4. Appuyez sur "Ajouter tous les événements"
            5. Les événements seront ajoutés à votre calendrier par défaut
            """)


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
        href = f'<a href="data:application/tcx+xml;base64,{b64}" download="training_plan_garmin.tcx">{translate("download_tcx", "plan_page")}</a>'
        st.markdown(href, unsafe_allow_html=True)


def handle_export_pdf(plan_controller: PlanController):
    """
    Gestionnaire pour l'export PDF

    Args:
        plan_controller: Contrôleur du plan d'entraînement
    """
    # Options par défaut simples pour l'export simple
    options = {
        "include_charts": True,
        "include_details": True,
        "paper_size": "A4",
        "orientation": "portrait"
    }

    pdf_data = plan_controller.export_to_pdf(options=options)

    if pdf_data:
        # Créer un lien de téléchargement
        b64 = base64.b64encode(pdf_data).decode()
        href = f'<a href="data:application/pdf;base64,{b64}" download="training_plan.pdf">{translate("download_pdf", "plan_page")}</a>'
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
        href = f'<a href="data:application/json;base64,{b64}" download="training_plan.json">{translate("download_json", "plan_page")}</a>'
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
            st.success(translate("import_success", "plan_page"))

            # Passer à l'affichage du plan
            st.session_state["view_mode"] = "calendar"
            st.rerun()
        else:
            st.error(translate("import_error", "plan_page"))

    except Exception as e:
        st.error(f"{translate('import_error', 'plan_page')}: {str(e)}")


def handle_adjust_plan(plan_controller: PlanController):
    """
    Gestionnaire pour l'ajustement du plan à la date courante

    Args:
        plan_controller: Contrôleur du plan d'entraînement
    """
    adjusted_plan = plan_controller.adjust_to_current_date()

    if adjusted_plan:
        st.session_state["current_plan"] = adjusted_plan
        st.success(translate("adjust_success", "plan_page"))
        st.rerun()
    else:
        st.error(translate("adjust_error", "plan_page"))


def handle_week_change(week_num: int):
    """
    Gestionnaire pour le changement de semaine

    Args:
        week_num: Numéro de la semaine à afficher
    """
    st.session_state["current_week"] = week_num

    # S'assurer que le plan est toujours marqué comme généré
    st.session_state["plan_generated"] = True


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
    # On supprime le plan actuel s'il existe
    del st.session_state["plan_generated"]

    # Vérifier si les données utilisateur sont présentes
    if "user_data" not in st.session_state:
        st.error(translate("no_user_data", "plan_page"))

        # Bouton pour retourner à la page d'entrée
        if st.button(translate("back_to_input", "plan_page")):
            del st.session_state["plan_generated"]
            st.session_state["page"] = "input"
            st.rerun()

        return

    with st.spinner(translate("generating_plan", "plan_page")):
        try:
            # Générer le plan
            plan = plan_controller.generate_plan(st.session_state["user_data"])

            if plan:
                # Afficher un message à l'utilisateur
                st.success(translate("plan_generated", "plan_page"))

                # Stocker le plan dans la session
                st.session_state["current_plan"] = plan

                # Marquer que le plan a été généré pour activer les boutons
                st.session_state["plan_generated"] = True

                # Initialiser la semaine courante
                if "current_week" not in st.session_state:
                    st.session_state["current_week"] = 0

                # Initialiser le mode d'affichage
                if "view_mode" not in st.session_state:
                    st.session_state["view_mode"] = "calendar"

                # Pour le débogage
                # st.write("Plan généré et stocké dans session_state")
                return plan
            else:
                st.error(translate("plan_generation_error", "plan_page"))
                return None
        except Exception as e:
            st.error(f"Erreur durant la génération du plan: {str(e)}")
            return None


def render_plan_summary(plan):
    st.header(translate("plan_summary", "plan_page"))

    col1, col2, col3 = st.columns([1, 1, 1])

    # Colonne 1: Informations de base
    with col1:
        st.subheader(translate("basic_info", "plan_page"))
        st.write(
            f"**{translate('start_date', 'plan_page')}:** {format_date(plan.user_data.start_date)}")
        st.write(
            f"**{translate('race_date', 'plan_page')}:** {format_date(plan.user_data.main_race.race_date)}")
        st.write(
            f"**{translate('race_type', 'plan_page')}:** {translate(plan.user_data.main_race.race_type.value, 'race_types')}")
        st.write(
            f"**{translate('total_weeks', 'plan_page')}:** {plan.user_data.total_weeks}")

    # Colonne 2: Statistiques d'entraînement
    with col2:
        st.subheader(translate("training_stats", "plan_page"))
        st.write(
            f"**{translate('total_volume', 'plan_page')}:** {plan.get_total_volume()} km")
        st.write(
            f"**{translate('total_duration', 'plan_page')}:** {format_timedelta(plan.get_total_duration(), 'hms_text')}")
        # Calculer la moyenne hebdomadaire
        avg_weekly_volume = plan.get_total_volume() / plan.user_data.total_weeks
        st.write(
            f"**{translate('avg_weekly_volume', 'plan_page')}:** {avg_weekly_volume:.1f} km")

    # Colonne 3: Répartition des séances
    with col3:
        st.subheader(translate("session_distribution", "plan_page"))
        sessions_by_type = {}
        for session in plan.sessions.values():
            if session.session_type != SessionType.REST:
                session_type = translate(
                    session.session_type.value, "session_types")
                sessions_by_type[session_type] = sessions_by_type.get(
                    session_type, 0) + 1

        for session_type, count in sessions_by_type.items():
            st.write(f"**{session_type}:** {count}")

    # Récapitulatif des phases
    st.subheader(translate("phase_overview", "plan_page"))
    phase_stats = plan.get_phase_stats()
    for phase, stats in phase_stats.items():
        phase_name = translate(phase.value, "phases")
        with st.expander(f"{phase_name} ({stats['start_date'].strftime('%d/%m')} - {stats['end_date'].strftime('%d/%m')})"):
            st.write(
                f"**{translate('duration', 'plan_page')}:** {stats['num_weeks']} {translate('weeks', 'common')}")
            st.write(
                f"**{translate('volume', 'plan_page')}:** {stats['total_volume']} km")
            st.write(
                f"**{translate('avg_weekly_volume', 'plan_page')}:** {stats['avg_weekly_volume']:.1f} km")


def render_export_import_section(plan_controller: PlanController):
    """
    Affiche la section d'export/import du plan
    """
    st.header(translate("export_import", "plan_page"))

    export_tab1, export_tab2, export_tab3, export_tab4 = st.tabs([
        "ICS/Calendrier", "PDF", "Données", "Garmin"
    ])

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        # Export ICS
        if st.button(translate("export_ics", "plan_page")):
            handle_export_ics(plan_controller)

    with col2:
        # Export PDF
        if st.button(translate("export_pdf", "plan_page")):
            handle_export_pdf(plan_controller)

    with col3:
        # Export JSON
        if st.button(translate("export_json", "plan_page")):
            handle_export_json(plan_controller)

    with col4:
        # Export TCX (pour Garmin)
        if st.button(translate("export_tcx", "plan_page")):
            handle_export_tcx(plan_controller)

    # Import JSON
    st.subheader(translate("import_plan", "plan_page"))

    uploaded_file = st.file_uploader(
        translate("upload_json", "plan_page"),
        type=["json"],
        help=translate("import_help", "plan_page")
    )

    if uploaded_file is not None:
        handle_import_json(plan_controller, uploaded_file)

    # Ajustement du plan
    st.subheader(translate("adjust_plan", "plan_page"))

    if st.button(translate("adjust_to_current_date", "plan_page")):
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
    render_week_calendar(plan, current_week,
                         on_session_click=handle_session_click)

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
    st.header(translate("plan_statistics", "plan_page"))

    # Timeline des phases
    render_phase_timeline(plan)

    # Graphiques
    col1, col2 = st.columns(2)

    with col1:
        render_volume_chart(
            plan, current_week=st.session_state.get("current_week"))
        render_phase_volume_distribution(plan)

    with col2:
        render_session_type_distribution(plan)
        render_training_load_chart(
            plan, current_week=st.session_state.get("current_week"))


def render_plan_view_page(plan_controller: PlanController):
    """
    Affiche la page de visualisation du plan d'entraînement

    Args:
        plan_controller: Contrôleur du plan d'entraînement
    """
    st.title(translate("plan_view_title", "plan_page"))

    # Vérifier si les données utilisateur ont été modifiées depuis la dernière génération
    user_data_hash = None
    if "user_data" in st.session_state:
        # Créer un hash des données utilisateur pour détecter les changements
        user_data_str = json.dumps(
            st.session_state["user_data"], sort_keys=True, default=str)
        user_data_hash = hashlib.md5(user_data_str.encode()).hexdigest()

    # Si les données ont changé, on force la régénération
    regenerate = False
    if user_data_hash and st.session_state.get("last_user_data_hash") != user_data_hash:
        regenerate = True
        st.session_state["last_user_data_hash"] = user_data_hash

    # Récupérer le plan actuel
    current_plan = None if regenerate else st.session_state.get("current_plan")

    if current_plan is None:
        # Générer le plan si les données utilisateur sont présentes
        current_plan = generate_plan(plan_controller)

        if current_plan is None:
            # Si aucun plan n'a pu être généré, on s'arrête ici
            st.session_state["plan_generated"] = False
            return

    # S'assurer que le plan est bien stocké en session
    st.session_state["current_plan"] = current_plan

    # Marquer que le plan a été généré pour activer les boutons
    st.session_state["plan_generated"] = True

    # À partir d'ici, on a un plan valide à afficher
    # Afficher un résumé du plan
    render_plan_summary(current_plan)

    # Tabs pour les différentes vues
    tab1, tab2, tab3 = st.tabs([
        translate("calendar", "plan_page"),
        translate("statistics", "plan_page"),
        translate("export", "plan_page"),
    ])

    with tab1:
        # Vue calendrier
        render_week_view(current_plan, st.session_state.get("current_week", 0))

    with tab2:
        # Vue statistique
        render_statistics_view(current_plan)

    with tab3:
        # Vue export (tableau)
        render_export_view(plan_controller)

    # Bouton pour revenir à la page d'entrée
    st.divider()

    if st.button(translate("back_to_input", "plan_page")):
        # Ne pas supprimer plan_generated pour garder les boutons actifs
        st.session_state["page"] = "input"
        st.rerun()


def render_export_view(plan_controller):
    """
    Affiche la section d'export et d'import du plan d'entraînement avec des options avancées.

    Args:
        plan_controller: Contrôleur du plan d'entraînement
    """
    import base64
    import pandas as pd
    from utils.date_utils import format_date
    from utils.time_converter import format_timedelta, format_pace

    st.header(translate("export_import", "plan_page"))

    # Options d'export sous forme d'onglets
    export_tab1, export_tab2, export_tab3, export_tab4 = st.tabs([
        translate("ics_calendar_export", "plan_page"),
        translate("pdf_export", "plan_page"),
        translate("data_export", "plan_page"),
        translate("device_export", "plan_page")
    ])

    with export_tab1:
        st.subheader(translate("ics_calendar_title", "plan_page"))

        # Options pour l'export ICS
        col1, col2 = st.columns(2)
        with col1:
            include_rest = st.checkbox(
                translate("include_rest_days", "plan_page"),
                value=False,
                help=translate("include_rest_help", "plan_page")
            )

            reminder_time = st.slider(
                translate("reminder_time", "plan_page"),
                min_value=0,
                max_value=120,
                value=30,
                step=5,
                help=translate("reminder_time_help", "plan_page")
            )

        with col2:
            start_time = st.slider(
                translate("default_start_time", "plan_page"),
                min_value=0,
                max_value=23,
                value=18,
                help=translate("default_start_time_help", "plan_page")
            )

            calendar_name = st.text_input(
                translate("calendar_name", "plan_page"),
                value="All-in-Run",
                help=translate("calendar_name_help", "plan_page")
            )

        # Bouton d'export avec options
        if st.button(translate("export_to_ics", "plan_page"), use_container_width=True):
            with st.spinner(translate("generating_ics", "plan_page")):
                ics_options = {
                    "include_rest_days": include_rest,
                    "reminder_time": reminder_time,
                    "start_time": start_time,
                    "ics_calendar_name": calendar_name
                }

                ics_data = plan_controller.export_to_ics(options=ics_options)

                if ics_data:
                    # Créer un lien de téléchargement
                    b64 = base64.b64encode(ics_data).decode()
                    filename = f"plan_entrainement_{calendar_name.replace(' ', '_')}.ics"
                    href = f'<a href="data:text/calendar;charset=utf-8;base64,{b64}" download="{filename}" class="download-link" target="_blank">{translate("download_ics", "plan_page")}</a>'

                    st.success(translate("ics_export_success", "plan_page"))
                    st.markdown(href, unsafe_allow_html=True)

                    # Ajouter des instructions sur comment l'importer
                    with st.expander(translate("ics_import_instructions", "plan_page")):
                        st.markdown(translate("ics_import_steps", "plan_page"))
                        st.markdown("""
                        ### Instructions spécifiques pour iPhone :
                        1. Téléchargez le fichier ICS
                        2. Appuyez sur le fichier téléchargé
                        3. Sélectionnez "Ouvrir dans Calendrier"
                        4. Appuyez sur "Ajouter tous les événements"
                        5. Les événements seront ajoutés à votre calendrier par défaut
                        """)
                else:
                    st.error(translate("export_error", "plan_page"))

    with export_tab2:
        st.subheader(translate("pdf_export_title", "plan_page"))

        # Options pour l'export PDF
        col1, col2 = st.columns(2)

        with col1:
            include_charts = st.checkbox(
                translate("include_charts", "plan_page"),
                value=True,
                help=translate("include_charts_help", "plan_page")
            )

            include_details = st.checkbox(
                translate("include_details", "plan_page"),
                value=True,
                help=translate("include_details_help", "plan_page")
            )

        with col2:
            paper_size = st.selectbox(
                translate("paper_size", "plan_page"),
                options=["A4", "Letter", "Legal"],
                index=0,
                help=translate("paper_size_help", "plan_page")
            )

            orientation = st.selectbox(
                translate("orientation", "plan_page"),
                options=[
                    translate("portrait", "plan_page"),
                    translate("landscape", "plan_page")
                ],
                index=0,
                help=translate("orientation_help", "plan_page")
            )

        # Bouton d'export PDF
        if st.button(translate("export_to_pdf", "plan_page"), use_container_width=True):
            with st.spinner(translate("generating_pdf", "plan_page")):
                pdf_options = {
                    "include_charts": include_charts,
                    "include_details": include_details,
                    "paper_size": paper_size,
                    "orientation": orientation.lower() if isinstance(orientation, str) else "portrait"
                }

                pdf_data = plan_controller.export_to_pdf(options=pdf_options)

                if pdf_data:
                    # Créer un lien de téléchargement
                    b64 = base64.b64encode(pdf_data).decode()
                    filename = "plan_entrainement.pdf"
                    href = f'<a href="data:application/pdf;base64,{b64}" download="{filename}" class="download-link">{translate("download_pdf", "plan_page")}</a>'

                    st.success(translate("pdf_export_success", "plan_page"))
                    st.markdown(href, unsafe_allow_html=True)
                else:
                    st.error(translate("export_error", "plan_page"))

    with export_tab3:
        st.subheader(translate("data_export_title", "plan_page"))

        # Options pour le format des données
        show_data_options = st.checkbox(
            translate("show_export_options", "plan_page"), value=True)

        if show_data_options:
            col1, col2 = st.columns(2)

            with col1:
                include_rest_days = st.checkbox(
                    translate("include_rest_days_export", "plan_page"),
                    value=False
                )

                include_phases = st.checkbox(
                    translate("include_phases", "plan_page"),
                    value=True
                )

            with col2:
                include_detailed_blocks = st.checkbox(
                    translate("include_detailed_blocks", "plan_page"),
                    value=True
                )

                sort_by = st.selectbox(
                    translate("sort_by", "plan_page"),
                    options=[
                        translate("date", "plan_page"),
                        translate("week_number", "plan_page"),
                        translate("distance", "plan_page")
                    ]
                )

        # Préparer les données du plan pour l'affichage et l'export
        if "current_plan" in st.session_state:
            plan = st.session_state["current_plan"]

            # Récupérer et formater les données du plan
            data = []
            for session_date, session in sorted(plan.sessions.items()):
                # Ignorer les jours de repos si l'option est désactivée
                if not include_rest_days and session.session_type == SessionType.REST:
                    continue

                # Calculer le numéro de semaine (1-indexed pour l'affichage)
                week_num = plan.get_week_number(session_date) + 1

                # Créer une ligne pour le tableau
                row = {
                    translate("week", "plan_page"): week_num,
                    translate("date", "plan_page"): format_date(session_date),
                    translate("type", "plan_page"): translate(session.session_type.value, "session_types"),
                    translate("distance", "plan_page"): f"{session.total_distance} km",
                    translate("duration", "plan_page"): format_timedelta(session.total_duration, "hms_text"),
                    translate("description", "plan_page"): session.description
                }

                # Ajouter la phase si l'option est activée
                if include_phases:
                    row[translate("phase", "plan_page")] = translate(
                        session.phase.value, "phases")

                # Ajouter les détails des blocs si l'option est activée
                if include_detailed_blocks and session.blocks:
                    block_details = []
                    for i, block in enumerate(session.blocks, 1):
                        block_details.append(
                            f"{block.distance} km @ {format_pace(block.pace)} ({block.description})"
                        )
                    row[translate("blocks", "plan_page")
                        ] = "; ".join(block_details)

                data.append(row)

            # Créer un DataFrame
            if data:
                df = pd.DataFrame(data)

                # Tri du DataFrame
                sort_column = translate("date", "plan_page")  # Par défaut
                if sort_by == translate("week_number", "plan_page"):
                    sort_column = translate("week", "plan_page")
                elif sort_by == translate("distance", "plan_page"):
                    # Pour trier par distance, on doit extraire les valeurs numériques
                    df[translate("distance_sort", "plan_page")] = df[translate(
                        "distance", "plan_page")].str.extract(r'(\d+\.?\d*)').astype(float)
                    sort_column = translate("distance_sort", "plan_page")

                df_sorted = df.sort_values(by=sort_column)

                # Afficher le tableau
                st.subheader(translate("plan_data_preview", "plan_page"))
                st.dataframe(
                    df_sorted.drop(columns=[translate("distance_sort", "plan_page")] if translate(
                        "distance_sort", "plan_page") in df_sorted.columns else []),
                    use_container_width=True
                )

                # Boutons d'export
                col1, col2 = st.columns(2)

                with col1:
                    if st.button(translate("export_to_json", "plan_page"), use_container_width=True):
                        with st.spinner(translate("generating_json", "plan_page")):
                            json_data = plan_controller.export_to_json()

                            if json_data:
                                # Créer un lien de téléchargement
                                b64 = base64.b64encode(
                                    json_data.encode('utf-8')).decode()
                                filename = "plan_entrainement.json"
                                href = f'<a href="data:application/json;base64,{b64}" download="{filename}" class="download-link">{translate("download_json", "plan_page")}</a>'

                                st.success(
                                    translate("json_export_success", "plan_page"))
                                st.markdown(href, unsafe_allow_html=True)
                            else:
                                st.error(
                                    translate("export_error", "plan_page"))

                with col2:
                    if st.button(translate("export_to_csv", "plan_page"), use_container_width=True):
                        with st.spinner(translate("generating_csv", "plan_page")):
                            # Exporter le DataFrame directement en CSV
                            csv = df_sorted.to_csv(index=False)

                            # Créer un lien de téléchargement
                            b64 = base64.b64encode(
                                csv.encode('utf-8')).decode()
                            filename = "plan_entrainement.csv"
                            href = f'<a href="data:text/csv;charset=utf-8;base64,{b64}" download="{filename}" class="download-link">{translate("download_csv", "plan_page")}</a>'

                            st.success(
                                translate("csv_export_success", "plan_page"))
                            st.markdown(href, unsafe_allow_html=True)
            else:
                st.warning(translate("no_data_to_export", "plan_page"))
        else:
            st.warning(translate("no_plan_generated", "plan_page"))

    with export_tab4:
        st.subheader(translate("device_export_title", "plan_page"))

        device_type = st.selectbox(
            translate("device_type", "plan_page"),
            options=["Apple Watch", "Garmin", "Suunto", "Polar", "Strava"],
            help=translate("device_type_help", "plan_page")
        )

        if device_type == "Garmin":
            st.info(translate("garmin_export_info", "plan_page"))

            if st.button(translate("export_to_tcx", "plan_page"), use_container_width=True):
                with st.spinner(translate("generating_tcx", "plan_page")):
                    tcx_data = plan_controller.export_to_tcx()

                    if tcx_data:
                        # Créer un lien de téléchargement
                        b64 = base64.b64encode(tcx_data).decode()
                        filename = "plan_entrainement_garmin.tcx"
                        href = f'<a href="data:application/vnd.garmin.tcx+xml;base64,{b64}" download="{filename}" class="download-link">{translate("download_tcx", "plan_page")}</a>'

                        st.success(
                            translate("tcx_export_success", "plan_page"))
                        st.markdown(href, unsafe_allow_html=True)

                        with st.expander(translate("garmin_import_instructions", "plan_page")):
                            st.markdown(
                                translate("garmin_import_steps", "plan_page"))
                    else:
                        st.error(translate("export_error", "plan_page"))

        elif device_type == "Apple Watch":
            st.info(translate("apple_export_info", "plan_page"))

            if st.button(translate("export_to_apple", "plan_page"), use_container_width=True):
                with st.spinner(translate("generating_apple_ics", "plan_page")):
                    apple_options = {
                        "calendar_name": "Workouts",
                        "include_rest_days": False,
                        "reminder_time": 15,
                        "start_time": 18
                    }

                    apple_ics_data = plan_controller.export_to_ics(
                        options=apple_options)

                    if apple_ics_data:
                        # Créer un lien de téléchargement
                        b64 = base64.b64encode(apple_ics_data).decode()
                        filename = "plan_entrainement_apple.ics"
                        href = f'<a href="data:text/calendar;charset=utf-8;base64,{b64}" download="{filename}" class="download-link">{translate("download_apple_ics", "plan_page")}</a>'

                        st.success(
                            translate("apple_export_success", "plan_page"))
                        st.markdown(href, unsafe_allow_html=True)

                        with st.expander(translate("apple_import_instructions", "plan_page")):
                            st.markdown(
                                translate("apple_import_steps", "plan_page"))
                    else:
                        st.error(translate("export_error", "plan_page"))

        elif device_type in ["Suunto", "Polar", "Strava"]:
            st.info(
                translate(f"{device_type.lower()}_export_info", "plan_page"))

            if st.button(translate(f"export_to_{device_type.lower()}", "plan_page"), use_container_width=True):
                st.warning(translate("feature_coming_soon", "plan_page"))
                st.info(translate("use_ics_instead", "plan_page"))

    # Section d'import
    st.markdown("---")
    st.subheader(translate("import_plan", "plan_page"))

    upload_col, info_col = st.columns([2, 3])

    with upload_col:
        uploaded_file = st.file_uploader(
            translate("upload_json", "plan_page"),
            type=["json"],
            help=translate("upload_json_help", "plan_page")
        )

        if uploaded_file is not None:
            if st.button(translate("import_plan_button", "plan_page"), use_container_width=True):
                with st.spinner(translate("importing_plan", "plan_page")):
                    try:
                        imported_plan = plan_controller.import_from_json(
                            uploaded_file)

                        if imported_plan:
                            st.session_state["current_plan"] = imported_plan
                            st.success(
                                translate("import_success", "plan_page"))

                            # Passer à l'affichage du plan
                            st.session_state["view_mode"] = "calendar"
                            st.rerun()
                        else:
                            st.error(translate("import_error", "plan_page"))
                    except Exception as e:
                        st.error(
                            f"{translate('import_error', 'plan_page')}: {str(e)}")

    with info_col:
        st.info(translate("import_info", "plan_page"))

        if 'current_plan' in st.session_state:
            st.write(translate("adjust_current_plan", "plan_page"))

            if st.button(translate("adjust_to_current_date", "plan_page")):
                with st.spinner(translate("adjusting_plan", "plan_page")):
                    adjusted_plan = plan_controller.adjust_to_current_date()

                    if adjusted_plan:
                        st.session_state["current_plan"] = adjusted_plan
                        st.success(translate("adjust_success", "plan_page"))
                        st.rerun()
                    else:
                        st.error(translate("adjust_error", "plan_page"))

    # Ajouter du CSS pour les liens de téléchargement
    st.markdown("""
    <style>
    .download-link {
        display: inline-block;
        background-color: #4CAF50;
        color: white;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        font-size: 16px;
        margin: 10px 0;
        border-radius: 5px;
        transition: background-color 0.3s;
    }
    
    .download-link:hover {
        background-color: #45a049;
    }
    </style>
    """, unsafe_allow_html=True)
