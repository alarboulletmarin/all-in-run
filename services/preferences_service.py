import json
import os
from typing import Dict, Any, Optional

class PreferencesService:
    """Service de gestion des préférences utilisateur"""

    def __init__(self, preferences_file: str = "user_preferences.json"):
        """
        Initialise le service de préférences

        Args:
            preferences_file: Chemin vers le fichier de préférences
        """
        self.preferences_file = preferences_file
        self.preferences = self._load_preferences()

    def _load_preferences(self) -> Dict[str, Any]:
        """
        Charge les préférences depuis le fichier

        Returns:
            Dictionnaire des préférences
        """
        if os.path.exists(self.preferences_file):
            try:
                with open(self.preferences_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return self._get_default_preferences()
        return self._get_default_preferences()

    def _get_default_preferences(self) -> Dict[str, Any]:
        """
        Retourne les préférences par défaut

        Returns:
            Dictionnaire des préférences par défaut
        """
        return {
            "export": {
                "ics": {
                    "include_rest_days": False,
                    "reminder_time": 30,
                    "start_time": 18,
                    "calendar_name": "All-in-Run",
                    "colors": {
                        "rest": "#f5f5f5",
                        "long_run": "#e3f2fd",
                        "threshold": "#fff3e0",
                        "ef": "#e8f5e9",
                        "race": "#ffebee"
                    }
                },
                "pdf": {
                    "include_charts": True,
                    "include_details": True,
                    "paper_size": "A4",
                    "orientation": "portrait"
                }
            },
            "ui": {
                "theme": "light",
                "show_tips": True,
                "display_mode": "calendar"
            }
        }

    def save_preferences(self) -> None:
        """Sauvegarde les préférences dans le fichier"""
        try:
            with open(self.preferences_file, 'w', encoding='utf-8') as f:
                json.dump(self.preferences, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des préférences: {e}")

    def get_export_preferences(self, export_type: str) -> Dict[str, Any]:
        """
        Récupère les préférences d'export

        Args:
            export_type: Type d'export (ics, pdf, etc.)

        Returns:
            Dictionnaire des préférences d'export
        """
        return self.preferences.get("export", {}).get(export_type, {})

    def update_export_preferences(self, export_type: str, preferences: Dict[str, Any]) -> None:
        """
        Met à jour les préférences d'export

        Args:
            export_type: Type d'export (ics, pdf, etc.)
            preferences: Nouvelles préférences
        """
        if "export" not in self.preferences:
            self.preferences["export"] = {}
        self.preferences["export"][export_type] = preferences
        self.save_preferences()

    def get_ui_preferences(self) -> Dict[str, Any]:
        """
        Récupère les préférences d'interface

        Returns:
            Dictionnaire des préférences d'interface
        """
        return self.preferences.get("ui", {})

    def update_ui_preferences(self, preferences: Dict[str, Any]) -> None:
        """
        Met à jour les préférences d'interface

        Args:
            preferences: Nouvelles préférences
        """
        self.preferences["ui"] = preferences
        self.save_preferences()

# Instance globale du service de préférences
preferences_service = PreferencesService() 