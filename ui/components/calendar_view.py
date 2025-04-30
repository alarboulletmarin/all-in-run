import streamlit as st
from datetime import datetime, timedelta
from utils.i18n import _ as translate
from services.preferences_service import preferences_service
from .drag_drop import render_drag_drop_calendar, handle_session_move
from .session_tags import render_session_tags, render_session_actions

def render_calendar_view():
    """
    Affiche la vue calendrier avec les séances d'entraînement
    """
    st.title(translate("calendar_view", "ui"))
    
    # Récupérer les préférences d'affichage
    ui_prefs = preferences_service.get_ui_preferences()
    
    # Sélecteur de période
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            translate("start_date", "ui"),
            value=datetime.now().date()
        )
    with col2:
        end_date = st.date_input(
            translate("end_date", "ui"),
            value=datetime.now().date() + timedelta(days=30)
        )
    
    # Vérifier que la date de fin est après la date de début
    if end_date < start_date:
        st.error(translate("invalid_date_range", "ui"))
        return
    
    # TODO: Récupérer les séances d'entraînement
    # Pour l'instant, on utilise des données d'exemple
    sample_sessions = [
        {
            "id": "1",
            "date": "2024-03-15",
            "type": translate("long_run", "sessions"),
            "duration": 60,
            "distance": 10,
            "notes": "",
            "tags": []
        },
        {
            "id": "2",
            "date": "2024-03-16",
            "type": translate("rest", "sessions"),
            "duration": 0,
            "distance": 0,
            "notes": "",
            "tags": []
        }
    ]
    
    # Afficher le calendrier avec glisser-déposer
    render_drag_drop_calendar(sample_sessions)
    
    # Gestion des messages du glisser-déposer
    if st.session_state.get("session_moved"):
        handle_session_move(
            st.session_state.session_moved["session_id"],
            st.session_state.session_moved["new_date"]
        )
        del st.session_state.session_moved
    
    # Sélection d'une séance
    selected_session = st.selectbox(
        translate("select_session", "ui"),
        options=[(s["id"], f"{s['date']} - {s['type']}") for s in sample_sessions],
        format_func=lambda x: x[1]
    )
    
    if selected_session:
        session_id = selected_session[0]
        session = next(s for s in sample_sessions if s["id"] == session_id)
        
        # Onglets pour les détails de la séance
        tab1, tab2 = st.tabs([
            translate("details", "ui"),
            translate("actions", "ui")
        ])
        
        with tab1:
            # Afficher les détails de la séance
            col1, col2 = st.columns(2)
            with col1:
                st.metric(translate("duration", "ui"), f"{session['duration']} min")
            with col2:
                st.metric(translate("distance", "ui"), f"{session['distance']} km")
            
            # Tags et notes
            render_session_tags(session_id)
        
        with tab2:
            # Actions sur la séance
            render_session_actions(session_id)
    
    # Bouton pour ajouter une nouvelle séance
    if st.button(translate("add_session", "ui")):
        st.session_state["show_session_form"] = True 