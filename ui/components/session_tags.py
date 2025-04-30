import streamlit as st
from utils.i18n import _ as translate

def render_session_tags(session_id=None):
    """
    Affiche l'interface de gestion des tags et notes d'une séance
    
    Args:
        session_id (str, optional): ID de la séance
    """
    st.subheader(translate("session_tags", "ui"))
    
    # Tags existants
    existing_tags = st.multiselect(
        translate("select_tags", "ui"),
        options=[
            translate("long_run", "tags"),
            translate("threshold", "tags"),
            translate("ef", "tags"),
            translate("race", "tags"),
            translate("rest", "tags"),
            translate("recovery", "tags"),
            translate("interval", "tags"),
            translate("hill", "tags"),
            translate("speed", "tags"),
            translate("endurance", "tags")
        ],
        help=translate("tags_help", "ui")
    )
    
    # Ajouter un nouveau tag
    new_tag = st.text_input(
        translate("add_new_tag", "ui"),
        help=translate("new_tag_help", "ui")
    )
    if new_tag and st.button(translate("add_tag", "ui")):
        # TODO: Ajouter le nouveau tag à la séance
        st.success(translate("tag_added", "ui"))
    
    # Notes personnelles
    st.subheader(translate("personal_notes", "ui"))
    notes = st.text_area(
        translate("session_notes", "ui"),
        help=translate("notes_help", "ui"),
        height=150
    )
    
    # Bouton de sauvegarde
    if st.button(translate("save_tags_notes", "ui")):
        # TODO: Sauvegarder les tags et notes
        st.success(translate("tags_notes_saved", "ui"))

def render_session_actions(session_id):
    """
    Affiche les actions disponibles pour une séance
    
    Args:
        session_id (str): ID de la séance
    """
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button(translate("duplicate_session", "ui")):
            # TODO: Dupliquer la séance
            st.success(translate("session_duplicated", "ui"))
    
    with col2:
        if st.button(translate("move_session", "ui")):
            # TODO: Activer le mode déplacement
            st.info(translate("drag_drop_mode", "ui"))
    
    with col3:
        if st.button(translate("delete_session", "ui")):
            # TODO: Supprimer la séance
            st.warning(translate("session_deleted", "ui")) 