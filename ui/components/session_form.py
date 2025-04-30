import streamlit as st
from datetime import datetime, time
from utils.i18n import _ as translate

def render_session_form():
    """
    Affiche le formulaire d'ajout de séance d'entraînement
    """
    st.title(translate("add_session", "ui"))
    
    # Formulaire
    with st.form("session_form"):
        # Date et heure
        col1, col2 = st.columns(2)
        with col1:
            session_date = st.date_input(
                translate("session_date", "ui"),
                value=datetime.now().date()
            )
        with col2:
            session_time = st.time_input(
                translate("session_time", "ui"),
                value=time(18, 0)  # 18h par défaut
            )
        
        # Type de séance
        session_type = st.selectbox(
            translate("session_type", "ui"),
            options=[
                translate("long_run", "sessions"),
                translate("threshold", "sessions"),
                translate("ef", "sessions"),
                translate("race", "sessions"),
                translate("rest", "sessions")
            ]
        )
        
        # Durée et distance
        col3, col4 = st.columns(2)
        with col3:
            duration = st.number_input(
                translate("duration", "ui"),
                min_value=0,
                max_value=600,
                value=60,
                help=translate("duration_help", "ui")
            )
        with col4:
            distance = st.number_input(
                translate("distance", "ui"),
                min_value=0.0,
                max_value=100.0,
                value=10.0,
                step=0.1,
                help=translate("distance_help", "ui")
            )
        
        # Notes
        notes = st.text_area(
            translate("notes", "ui"),
            help=translate("notes_help", "ui")
        )
        
        # Boutons
        col5, col6 = st.columns(2)
        with col5:
            submit = st.form_submit_button(translate("save", "ui"))
        with col6:
            if st.form_submit_button(translate("cancel", "ui")):
                st.session_state["show_session_form"] = False
        
        if submit:
            # TODO: Sauvegarder la séance
            st.success(translate("session_saved", "ui"))
            st.session_state["show_session_form"] = False 