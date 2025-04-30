import json
import os
from typing import Dict, Any, Optional
import streamlit as st

from config.languages import DEFAULT_LANGUAGE, AVAILABLE_LANGUAGES


class I18n:
    """Gestionnaire d'internationalisation pour l'application"""

    def __init__(self, locale_dir: str = "i18n"):
        """
        Initialise le gestionnaire d'internationalisation

        Args:
            locale_dir: Chemin vers le répertoire contenant les fichiers de traduction
        """
        self.locale_dir = locale_dir
        self.translations: Dict[str, Dict[str, Dict[str, str]]] = {}

        # Initialiser avec des dictionnaires vides pour chaque langue
        for lang_code, _ in AVAILABLE_LANGUAGES:
            self.translations[lang_code] = {
                "common": {},
                "input_page": {},
                "plan_page": {},
                "simulation_page": {},
                "calendar": {},
                "charts": {},
                "forms": {},
                "session_types": {},
                "phases": {},
                "race_types": {},
                "intensity": {},
                "export": {
                    "export_title": "Export" if lang_code == "fr" else "Export" if lang_code == "en" else "Exportar",
                    "export_description": "Exportez votre plan d'entraînement" if lang_code == "fr" else "Export your training plan" if lang_code == "en" else "Exporta tu plan de entrenamiento"
                }
            }

        # Essayer de charger les traductions disponibles
        try:
            self._load_all_translations()
        except Exception as e:
            print(f"Erreur lors du chargement des traductions: {e}")
            # Créer des fichiers de traduction par défaut si nécessaire
            self._create_default_translations()

    def _create_default_translations(self) -> None:
        """Crée des fichiers de traduction par défaut si nécessaire"""
        # Créer le dossier i18n s'il n'existe pas
        if not os.path.exists(self.locale_dir):
            os.makedirs(self.locale_dir)

        # Créer les sous-dossiers pour chaque langue
        for lang_code, _ in AVAILABLE_LANGUAGES:
            lang_dir = os.path.join(self.locale_dir, lang_code)
            if not os.path.exists(lang_dir):
                os.makedirs(lang_dir)

            # Créer un fichier common.json par défaut
            common_file = os.path.join(lang_dir, "common.json")
            if not os.path.exists(common_file):
                default_common = {
                    "app_title": "All-in-Run",
                    "app_subtitle": "Generate your training plan" if lang_code == "en" else "Générez votre plan d'entraînement" if lang_code == "fr" else "Genera tu plan de entrenamiento",
                    # Ajout des instructions d'importation ICS pour les différentes langues
                    "ics_import_steps": """
                    ## How to import your training plan into your calendar

                    1. Download the ICS file using the link above
                    2. For Google Calendar:
                       - Open Google Calendar
                       - Click on the "+" button next to "Other calendars"
                       - Select "Import"
                       - Upload the downloaded ICS file
                       - Click "Import"
                    3. For Apple Calendar:
                       - Open Calendar app
                       - Select "File" > "Import"
                       - Choose the downloaded ICS file
                       - Click "Import"
                    4. For Outlook:
                       - Open Outlook
                       - Go to Calendar view
                       - Select "File" > "Import & Export" > "Import an iCalendar (.ics)"
                       - Browse to the downloaded file
                       - Click "Open"
                    """ if lang_code == "en" else """
                    ## Comment importer votre plan d'entraînement dans votre calendrier

                    1. Téléchargez le fichier ICS via le lien ci-dessus
                    2. Pour Google Agenda :
                       - Ouvrez Google Agenda
                       - Cliquez sur le bouton "+" à côté de "Autres agendas"
                       - Sélectionnez "Importer"
                       - Téléchargez le fichier ICS téléchargé
                       - Cliquez sur "Importer"
                    3. Pour Apple Calendrier :
                       - Ouvrez l'application Calendrier
                       - Sélectionnez "Fichier" > "Importer"
                       - Choisissez le fichier ICS téléchargé
                       - Cliquez sur "Importer"
                    4. Pour Outlook :
                       - Ouvrez Outlook
                       - Allez à la vue Calendrier
                       - Sélectionnez "Fichier" > "Importer et exporter" > "Importer un iCalendar (.ics)"
                       - Naviguez jusqu'au fichier téléchargé
                       - Cliquez sur "Ouvrir"
                    """ if lang_code == "fr" else """
                    ## Cómo importar su plan de entrenamiento a su calendario

                    1. Descargue el archivo ICS usando el enlace de arriba
                    2. Para Google Calendar:
                       - Abra Google Calendar
                       - Haga clic en el botón "+" junto a "Otros calendarios"
                       - Seleccione "Importar"
                       - Suba el archivo ICS descargado
                       - Haga clic en "Importar"
                    3. Para Apple Calendar:
                       - Abra la aplicación Calendario
                       - Seleccione "Archivo" > "Importar"
                       - Elija el archivo ICS descargado
                       - Haga clic en "Importar"
                    4. Para Outlook:
                       - Abra Outlook
                       - Vaya a la vista Calendario
                       - Seleccione "Archivo" > "Importar y Exportar" > "Importar un iCalendar (.ics)"
                       - Navegue hasta el archivo
                       - Haga clic en "Abrir"
                    """,
                    
                    # Nouvelles traductions pour l'export ICS
                    "day_0": "Lundi" if lang_code == "fr" else "Monday" if lang_code == "en" else "Lunes",
                    "day_1": "Mardi" if lang_code == "fr" else "Tuesday" if lang_code == "en" else "Martes",
                    "day_2": "Mercredi" if lang_code == "fr" else "Wednesday" if lang_code == "en" else "Miércoles",
                    "day_3": "Jeudi" if lang_code == "fr" else "Thursday" if lang_code == "en" else "Jueves",
                    "day_4": "Vendredi" if lang_code == "fr" else "Friday" if lang_code == "en" else "Viernes",
                    "day_5": "Samedi" if lang_code == "fr" else "Saturday" if lang_code == "en" else "Sábado",
                    "day_6": "Dimanche" if lang_code == "fr" else "Sunday" if lang_code == "en" else "Domingo",
                    "rest_day": "Jour de repos" if lang_code == "fr" else "Rest day" if lang_code == "en" else "Día de descanso"
                }

                with open(common_file, 'w', encoding='utf-8') as f:
                    json.dump(default_common, f, indent=2, ensure_ascii=False)

    def _load_all_translations(self) -> None:
        """Charge toutes les traductions disponibles"""
        for lang_code, _ in AVAILABLE_LANGUAGES:
            lang_dir = os.path.join(self.locale_dir, lang_code)

            if os.path.exists(lang_dir):
                for file_name in os.listdir(lang_dir):
                    if file_name.endswith('.json'):
                        file_path = os.path.join(lang_dir, file_name)
                        namespace = os.path.splitext(file_name)[0]

                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                self.translations[lang_code][namespace] = json.load(f)
                        except Exception as e:
                            print(f"Erreur lors du chargement de {file_path}: {e}")
                            # Garder un dictionnaire vide pour ce namespace
                            self.translations[lang_code][namespace] = {}

    def get_text(self, key: str, namespace: str = "common", lang: Optional[str] = None) -> str:
        """
        Obtient un texte traduit

        Args:
            key: Clé de traduction
            namespace: Namespace (fichier) de traduction
            lang: Code de langue, si None utilise la langue en session

        Returns:
            Texte traduit ou clé si traduction non trouvée
        """
        # Utiliser la langue en session ou la langue par défaut
        selected_lang = lang or st.session_state.get("language", DEFAULT_LANGUAGE)

        # Vérifier si la langue est disponible, sinon utiliser la langue par défaut
        if selected_lang not in self.translations:
            selected_lang = DEFAULT_LANGUAGE

        # Vérifier si le namespace existe
        if namespace not in self.translations[selected_lang]:
            # Essayer avec la langue par défaut
            if namespace in self.translations[DEFAULT_LANGUAGE]:
                return self.translations[DEFAULT_LANGUAGE][namespace].get(key, key)
            return key

        # Retourner la traduction ou la clé si non trouvée
        return self.translations[selected_lang][namespace].get(key, key)

    def switch_language(self, lang_code: str) -> None:
        """
        Change la langue courante

        Args:
            lang_code: Code de la langue à utiliser
        """
        available_codes = [code for code, _ in AVAILABLE_LANGUAGES]
        if lang_code in available_codes:
            st.session_state["language"] = lang_code
        else:
            st.session_state["language"] = DEFAULT_LANGUAGE

    def get_current_language(self) -> str:
        """
        Obtient le code de la langue courante

        Returns:
            Code de la langue courante
        """
        return st.session_state.get("language", DEFAULT_LANGUAGE)

    def get_language_name(self, lang_code: Optional[str] = None) -> str:
        """
        Obtient le nom de la langue à partir de son code

        Args:
            lang_code: Code de la langue, si None utilise la langue courante

        Returns:
            Nom de la langue
        """
        code = lang_code or self.get_current_language()
        for available_code, name in AVAILABLE_LANGUAGES:
            if available_code == code:
                return name
        return ""


# Créer une instance globale du gestionnaire d'i18n
i18n = I18n()

# Alias pour get_text pour simplifier l'utilisation
def _(key: str, namespace: str = "common") -> str:
    """
    Fonction raccourcie pour obtenir un texte traduit

    Args:
        key: Clé de traduction
        namespace: Namespace de traduction

    Returns:
        Texte traduit
    """
    return i18n.get_text(key, namespace)