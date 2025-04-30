import streamlit as st
from utils.i18n import _ as translate

def render_tooltip(text, icon="ℹ️"):
    """
    Affiche une infobulle avec le texte d'aide
    
    Args:
        text (str): Le texte d'aide à afficher
        icon (str): L'icône à utiliser (par défaut: ℹ️)
    """
    st.markdown(f"""
    <style>
    .tooltip {{
        position: relative;
        display: inline-block;
        cursor: help;
    }}
    .tooltip .tooltiptext {{
        visibility: hidden;
        width: 200px;
        background-color: #555;
        color: #fff;
        text-align: center;
        border-radius: 6px;
        padding: 5px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transition: opacity 0.3s;
    }}
    .tooltip:hover .tooltiptext {{
        visibility: visible;
        opacity: 1;
    }}
    </style>
    
    <div class="tooltip">
        {icon}
        <span class="tooltiptext">{text}</span>
    </div>
    """, unsafe_allow_html=True)

def render_help_section():
    """
    Affiche une section d'aide avec des infobulles pour les fonctionnalités principales
    """
    st.markdown("### " + translate("help_section", "ui"))
    
    # Fonctionnalités principales
    features = [
        {
            "title": translate("calendar_view", "help"),
            "description": translate("calendar_view_description", "help"),
            "icon": "📅"
        },
        {
            "title": translate("statistics_view", "help"),
            "description": translate("statistics_view_description", "help"),
            "icon": "📊"
        },
        {
            "title": translate("export_features", "help"),
            "description": translate("export_features_description", "help"),
            "icon": "📤"
        },
        {
            "title": translate("preferences", "help"),
            "description": translate("preferences_description", "help"),
            "icon": "⚙️"
        }
    ]
    
    for feature in features:
        col1, col2 = st.columns([1, 4])
        with col1:
            render_tooltip(feature["description"], feature["icon"])
        with col2:
            st.markdown(f"**{feature['title']}**") 