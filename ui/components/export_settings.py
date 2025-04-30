import streamlit as st
from utils.i18n import _ as translate
from services.preferences_service import preferences_service

def render_export_settings():
    """
    Affiche les paramètres d'export des séances d'entraînement
    """
    st.title(translate("export_settings", "ui"))
    
    # Récupérer les préférences d'export
    export_prefs = preferences_service.get_export_preferences("ics")
    
    # Paramètres d'export ICS
    st.subheader(translate("ics_export", "ui"))
    
    with st.expander(translate("ics_settings", "ui")):
        # Nom du calendrier
        calendar_name = st.text_input(
            translate("calendar_name", "ui"),
            value=export_prefs.get("calendar_name", "All-in-Run")
        )
        
        # Heure de début par défaut
        start_time = st.time_input(
            translate("default_start_time", "ui"),
            value=export_prefs.get("start_time", "18:00")
        )
        
        # Temps de rappel
        reminder_time = st.number_input(
            translate("reminder_time", "ui"),
            min_value=0,
            max_value=1440,
            value=export_prefs.get("reminder_time", 30),
            help=translate("reminder_time_help", "ui")
        )
        
        # Inclure les jours de repos
        include_rest_days = st.checkbox(
            translate("include_rest_days", "ui"),
            value=export_prefs.get("include_rest_days", False)
        )
        
        # Couleurs des types de séances
        st.markdown("### " + translate("session_colors", "ui"))
        colors = export_prefs.get("colors", {})
        
        col1, col2 = st.columns(2)
        with col1:
            colors["rest"] = st.color_picker(
                translate("rest_color", "ui"),
                value=colors.get("rest", "#f5f5f5")
            )
            colors["long_run"] = st.color_picker(
                translate("long_run_color", "ui"),
                value=colors.get("long_run", "#e3f2fd")
            )
            colors["threshold"] = st.color_picker(
                translate("threshold_color", "ui"),
                value=colors.get("threshold", "#fff3e0")
            )
        with col2:
            colors["ef"] = st.color_picker(
                translate("ef_color", "ui"),
                value=colors.get("ef", "#e8f5e9")
            )
            colors["race"] = st.color_picker(
                translate("race_color", "ui"),
                value=colors.get("race", "#ffebee")
            )
    
    # Paramètres d'export PDF
    st.subheader(translate("pdf_export", "ui"))
    
    with st.expander(translate("pdf_settings", "ui")):
        pdf_prefs = preferences_service.get_export_preferences("pdf")
        
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
    
    # Bouton de sauvegarde
    if st.button(translate("save_settings", "ui")):
        # Mettre à jour les préférences ICS
        preferences_service.update_export_preferences("ics", {
            "calendar_name": calendar_name,
            "start_time": start_time.strftime("%H:%M"),
            "reminder_time": reminder_time,
            "include_rest_days": include_rest_days,
            "colors": colors
        })
        
        # Mettre à jour les préférences PDF
        preferences_service.update_export_preferences("pdf", {
            "paper_size": paper_size,
            "orientation": orientation,
            "include_charts": include_charts,
            "include_details": include_details
        })
        
        st.success(translate("settings_saved", "ui")) 