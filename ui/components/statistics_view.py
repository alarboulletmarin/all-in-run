import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.i18n import _ as translate
from services.preferences_service import preferences_service

def render_statistics_view():
    """
    Affiche la vue statistiques avec les analyses des séances d'entraînement
    """
    st.title(translate("statistics_view", "ui"))
    
    # Récupérer les préférences d'affichage
    ui_prefs = preferences_service.get_ui_preferences()
    
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
    
    # TODO: Récupérer les données des séances
    # Pour l'instant, on utilise des données d'exemple
    sample_data = {
        "dates": [
            datetime.now().date() - timedelta(days=i) 
            for i in range(30)
        ],
        "distances": [10, 5, 0, 15, 8, 0, 12, 6, 0, 20] * 3,
        "durations": [60, 30, 0, 90, 45, 0, 75, 40, 0, 120] * 3,
        "types": ["long_run", "threshold", "rest", "ef", "threshold", "rest", "long_run", "ef", "rest", "race"] * 3
    }
    
    # Onglets pour différents types de statistiques
    tab1, tab2, tab3 = st.tabs([
        translate("weekly_summary", "stats"),
        translate("type_analysis", "stats"),
        translate("progress", "stats")
    ])
    
    with tab1:
        st.subheader(translate("weekly_summary", "stats"))
        
        # Graphique de distance hebdomadaire
        fig_distance = px.bar(
            x=sample_data["dates"],
            y=sample_data["distances"],
            labels={
                "x": translate("date", "ui"),
                "y": translate("distance", "ui") + " (km)"
            }
        )
        st.plotly_chart(fig_distance, use_container_width=True)
        
        # Graphique de durée hebdomadaire
        fig_duration = px.bar(
            x=sample_data["dates"],
            y=sample_data["durations"],
            labels={
                "x": translate("date", "ui"),
                "y": translate("duration", "ui") + " (min)"
            }
        )
        st.plotly_chart(fig_duration, use_container_width=True)
    
    with tab2:
        st.subheader(translate("type_analysis", "stats"))
        
        # Distribution des types de séances
        type_counts = {}
        for session_type in sample_data["types"]:
            type_counts[session_type] = type_counts.get(session_type, 0) + 1
        
        fig_types = px.pie(
            values=list(type_counts.values()),
            names=list(type_counts.keys()),
            title=translate("session_types_distribution", "stats")
        )
        st.plotly_chart(fig_types, use_container_width=True)
    
    with tab3:
        st.subheader(translate("progress", "stats"))
        
        # Progression de la distance
        fig_progress = go.Figure()
        fig_progress.add_trace(go.Scatter(
            x=sample_data["dates"],
            y=sample_data["distances"],
            mode='lines+markers',
            name=translate("distance", "ui")
        ))
        fig_progress.update_layout(
            title=translate("distance_progress", "stats"),
            xaxis_title=translate("date", "ui"),
            yaxis_title=translate("distance", "ui") + " (km)"
        )
        st.plotly_chart(fig_progress, use_container_width=True)
        
        # Statistiques résumées
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                translate("total_distance", "stats"),
                f"{sum(sample_data['distances'])} km"
            )
        with col2:
            st.metric(
                translate("average_distance", "stats"),
                f"{sum(sample_data['distances'])/len(sample_data['distances']):.1f} km"
            )
        with col3:
            st.metric(
                translate("total_duration", "stats"),
                f"{sum(sample_data['durations'])} min"
            ) 