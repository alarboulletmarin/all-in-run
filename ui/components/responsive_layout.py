import streamlit as st
from typing import List, Callable, Dict, Any, Union, Optional

def responsive_columns(ratios: List[int] = None, gap: str = "small", mobile_breakpoint: int = 768) -> List[st.container]:
    """
    Crée des colonnes responsives qui s'adaptent aux petits écrans.
    Sur mobile, les colonnes s'empilent verticalement.

    Args:
        ratios: Liste des ratios de largeur (par défaut égaux)
        gap: Espace entre les colonnes ("small", "medium", "large")
        mobile_breakpoint: Largeur d'écran (px) en dessous de laquelle les colonnes s'empilent

    Returns:
        Liste de conteneurs pour chaque colonne
    """
    # Définir les ratios par défaut si non fournis
    if ratios is None:
        ratios = [1] * 2  # 2 colonnes égales par défaut
    
    # Calculer la largeur totale
    total = sum(ratios)
    widths = [r / total for r in ratios]
    
    # Définir les classes CSS pour l'espacement
    gap_class = {
        "small": "gap-2",
        "medium": "gap-4",
        "large": "gap-8"
    }.get(gap, "gap-4")
    
    # Injecter le CSS pour la mise en page responsive
    st.markdown(f"""
    <style>
    .responsive-columns {{
        display: flex;
        flex-direction: row;
        {gap_class};
        width: 100%;
    }}
    
    @media (max-width: {mobile_breakpoint}px) {{
        .responsive-columns {{
            flex-direction: column;
        }}
        .responsive-column {{
            width: 100% !important;
            margin-bottom: 1rem;
        }}
    }}
    </style>
    """, unsafe_allow_html=True)
    
    # Créer le conteneur de colonnes
    columns_html = '<div class="responsive-columns">'
    for width in widths:
        columns_html += f'<div class="responsive-column" style="width: {width*100}%"></div>'
    columns_html += '</div>'
    
    st.markdown(columns_html, unsafe_allow_html=True)
    
    # Utiliser streamlit.columns comme base
    return st.columns(ratios)

def responsive_grid(items: List[Any], 
                   renderer: Callable[[Any], None], 
                   cols_desktop: int = 3, 
                   cols_tablet: int = 2, 
                   cols_mobile: int = 1,
                   tablet_breakpoint: int = 992, 
                   mobile_breakpoint: int = 576) -> None:
    """
    Affiche les éléments dans une grille responsive qui s'adapte à la taille de l'écran.

    Args:
        items: Liste des éléments à afficher dans la grille
        renderer: Fonction qui prend un élément et le rend dans l'interface
        cols_desktop: Nombre de colonnes sur desktop
        cols_tablet: Nombre de colonnes sur tablette
        cols_mobile: Nombre de colonnes sur mobile
        tablet_breakpoint: Largeur d'écran (px) en dessous de laquelle passer en mode tablette
        mobile_breakpoint: Largeur d'écran (px) en dessous de laquelle passer en mode mobile
    """
    # Injecter le CSS pour la grille responsive
    st.markdown(f"""
    <style>
    .responsive-grid {{
        display: grid;
        grid-template-columns: repeat({cols_desktop}, 1fr);
        gap: 1rem;
        width: 100%;
    }}
    
    @media (max-width: {tablet_breakpoint}px) {{
        .responsive-grid {{
            grid-template-columns: repeat({cols_tablet}, 1fr);
        }}
    }}
    
    @media (max-width: {mobile_breakpoint}px) {{
        .responsive-grid {{
            grid-template-columns: repeat({cols_mobile}, 1fr);
        }}
    }}
    </style>
    """, unsafe_allow_html=True)
    
    # Créer des conteneurs pour chaque élément
    with st.container():
        st.markdown('<div class="responsive-grid">', unsafe_allow_html=True)
        
        # Utiliser colonnes de Streamlit comme base
        cols = st.columns(cols_desktop)
        
        for i, item in enumerate(items):
            with cols[i % cols_desktop]:
                renderer(item)
        
        st.markdown('</div>', unsafe_allow_html=True)

def responsive_container(max_width: str = "1200px", padding: str = "1rem") -> None:
    """
    Crée un conteneur responsive avec une largeur maximale.

    Args:
        max_width: Largeur maximale du conteneur
        padding: Marge intérieure du conteneur
    """
    st.markdown(f"""
    <style>
    .reportview-container .main .block-container {{
        max-width: {max_width};
        padding: {padding};
        margin: 0 auto;
    }}
    </style>
    """, unsafe_allow_html=True)

def card(title: str, content: Any, footer: Optional[str] = None, is_expanded: bool = False) -> None:
    """
    Affiche un composant carte responsive avec titre, contenu et pied de page optionnel.

    Args:
        title: Titre de la carte
        content: Contenu de la carte (chaîne, fonction ou autre)
        footer: Pied de page de la carte (optionnel)
        is_expanded: Si la carte doit être développée par défaut
    """
    with st.expander(title, expanded=is_expanded):
        # Si le contenu est une fonction, l'appeler
        if callable(content):
            content()
        else:
            st.write(content)
        
        # Afficher le pied de page s'il existe
        if footer:
            st.markdown(f"<div style='text-align: right; font-size: 0.8em; margin-top: 10px;'>{footer}</div>", 
                        unsafe_allow_html=True)

def adaptive_form(fields: List[Dict[str, Any]], 
                 cols_desktop: int = 2, 
                 cols_mobile: int = 1,
                 mobile_breakpoint: int = 768) -> None:
    """
    Crée un formulaire qui s'adapte à la taille de l'écran.
    
    Args:
        fields: Liste de dictionnaires avec les champs du formulaire
        cols_desktop: Nombre de colonnes sur desktop
        cols_mobile: Nombre de colonnes sur mobile
        mobile_breakpoint: Largeur d'écran (px) en dessous de laquelle passer en mode mobile
    """
    # Injecter le CSS pour le formulaire responsive
    st.markdown(f"""
    <style>
    .form-row {{
        display: grid;
        grid-template-columns: repeat({cols_desktop}, 1fr);
        gap: 1rem;
        margin-bottom: 1rem;
    }}
    
    @media (max-width: {mobile_breakpoint}px) {{
        .form-row {{
            grid-template-columns: repeat({cols_mobile}, 1fr);
        }}
    }}
    </style>
    """, unsafe_allow_html=True)
    
    # Grouper les champs en rangées
    rows = [fields[i:i+cols_desktop] for i in range(0, len(fields), cols_desktop)]
    
    # Afficher chaque rangée
    for row in rows:
        cols = st.columns(cols_desktop)
        for i, field in enumerate(row):
            with cols[i]:
                field_type = field.get('type', 'text')
                if field_type == 'text':
                    st.text_input(
                        field.get('label', ''),
                        value=field.get('value', ''),
                        key=field.get('key'),
                        help=field.get('help'),
                        disabled=field.get('disabled', False)
                    )
                elif field_type == 'number':
                    st.number_input(
                        field.get('label', ''),
                        min_value=field.get('min'),
                        max_value=field.get('max'),
                        value=field.get('value'),
                        step=field.get('step', 1),
                        key=field.get('key'),
                        help=field.get('help'),
                        disabled=field.get('disabled', False)
                    )
                elif field_type == 'date':
                    st.date_input(
                        field.get('label', ''),
                        value=field.get('value'),
                        key=field.get('key'),
                        help=field.get('help'),
                        disabled=field.get('disabled', False)
                    )
                elif field_type == 'select':
                    st.selectbox(
                        field.get('label', ''),
                        options=field.get('options', []),
                        index=field.get('index', 0),
                        key=field.get('key'),
                        help=field.get('help'),
                        disabled=field.get('disabled', False)
                    )
                elif field_type == 'slider':
                    st.slider(
                        field.get('label', ''),
                        min_value=field.get('min'),
                        max_value=field.get('max'),
                        value=field.get('value'),
                        step=field.get('step', 1),
                        key=field.get('key'),
                        help=field.get('help'),
                        disabled=field.get('disabled', False)
                    )
