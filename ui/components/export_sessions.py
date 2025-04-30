import streamlit as st
from datetime import datetime, timedelta
from utils.i18n import _ as translate
from services.preferences_service import preferences_service

def render_export_sessions():
    """
    Affiche l'interface d'export des séances d'entraînement
    """
    st.title(translate("export_sessions", "ui"))
    
    # Sélecteur de période
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            translate("start_date", "ui"),
            value=datetime.now().date() - timedelta(days=30)
        )
    with col2:
        end_date = st.date_input(
            translate("end_date", "ui"),
            value=datetime.now().date()
        )
    
    # Vérifier que la date de fin est après la date de début
    if end_date < start_date:
        st.error(translate("invalid_date_range", "ui"))
        return
    
    # Type d'export
    st.subheader(translate("export_type", "ui"))
    export_type = st.radio(
        translate("select_export_type", "ui"),
        options=["ics", "pdf"],
        help=translate("export_type_help", "ui")
    )
    
    if export_type == "ics":
        render_ics_export(start_date, end_date)
    else:
        render_pdf_export(start_date, end_date)

def render_ics_export(start_date, end_date):
    """
    Affiche les options d'export ICS
    
    Args:
        start_date: Date de début
        end_date: Date de fin
    """
    # Récupérer les préférences ICS
    ics_prefs = preferences_service.get_export_preferences("ics")
    
    # Options d'export
    st.markdown("### " + translate("export_options", "ui"))
    
    # Inclure les jours de repos
    include_rest_days = st.checkbox(
        translate("include_rest_days", "ui"),
        value=ics_prefs.get("include_rest_days", False)
    )
    
    # Bouton d'export
    if st.button(translate("export_ics", "ui")):
        # TODO: Générer et télécharger le fichier ICS
        st.success(translate("export_success", "ui"))

def render_pdf_export(start_date, end_date):
    """
    Affiche les options d'export PDF
    
    Args:
        start_date: Date de début
        end_date: Date de fin
    """
    # Récupérer les préférences PDF
    pdf_prefs = preferences_service.get_export_preferences("pdf")
    
    # Options d'export
    st.markdown("### " + translate("export_options", "ui"))
    
    # Inclure les graphiques
    include_charts = st.checkbox(
        translate("include_charts", "ui"),
        value=pdf_prefs.get("include_charts", True)
    )
    
    # Inclure les détails
    include_details = st.checkbox(
        translate("include_details", "ui"),
        value=pdf_prefs.get("include_details", True)
    )
    
    # Format du papier
    paper_size = st.selectbox(
        translate("paper_size", "ui"),
        options=["A4", "A5", "Letter"],
        index=["A4", "A5", "Letter"].index(pdf_prefs.get("paper_size", "A4"))
    )
    
    # Orientation
    orientation = st.radio(
        translate("orientation", "ui"),
        options=["portrait", "landscape"],
        index=["portrait", "landscape"].index(pdf_prefs.get("orientation", "portrait"))
    )
    
    # Bouton d'export
    if st.button(translate("export_pdf", "ui")):
        # TODO: Générer et télécharger le fichier PDF
        st.success(translate("export_success", "ui")) 