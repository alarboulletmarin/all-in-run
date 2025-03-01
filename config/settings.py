"""
Paramètres configurables pour l'application All-in-Run.
"""
import os
from typing import Dict, Any
import json


class Settings:
    """Gestion des paramètres de l'application"""

    def __init__(self, config_file: str = None):
        """
        Initialise les paramètres avec des valeurs par défaut

        Args:
            config_file: Chemin vers un fichier de configuration JSON (optionnel)
        """
        # Paramètres de l'interface utilisateur
        self.ui = {
            "theme": "light",
            "show_tips": True,
            "display_mode": "calendar",  # 'calendar' ou 'list'
        }

        # Paramètres pour les exports
        self.export = {
            "ics_calendar_name": "All-in-Run",
            "pdf_include_charts": True,
            "pdf_include_stats": True,
        }

        # Paramètres de notification (pour version future)
        self.notifications = {
            "enabled": False,
            "reminder_days": 1,  # Nombre de jours avant la séance pour le rappel
        }

        # Si un fichier de configuration est fourni, charger les paramètres
        if config_file and os.path.exists(config_file):
            self.load_from_file(config_file)

    def load_from_file(self, config_file: str) -> None:
        """
        Charge les paramètres depuis un fichier JSON

        Args:
            config_file: Chemin vers le fichier de configuration
        """
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)

            # Mettre à jour les paramètres avec les valeurs du fichier
            if "ui" in config_data:
                self.ui.update(config_data["ui"])
            if "export" in config_data:
                self.export.update(config_data["export"])
            if "notifications" in config_data:
                self.notifications.update(config_data["notifications"])

        except (json.JSONDecodeError, IOError) as e:
            # En cas d'erreur, utiliser les valeurs par défaut
            print(f"Erreur lors du chargement des paramètres: {e}")

    def save_to_file(self, config_file: str) -> None:
        """
        Sauvegarde les paramètres dans un fichier JSON

        Args:
            config_file: Chemin vers le fichier de configuration
        """
        config_data = {
            "ui": self.ui,
            "export": self.export,
            "notifications": self.notifications,
        }

        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2)
        except IOError as e:
            print(f"Erreur lors de la sauvegarde des paramètres: {e}")

    def get_value(self, section: str, key: str, default: Any = None) -> Any:
        """
        Récupère une valeur de paramètre

        Args:
            section: Section du paramètre (ui, export, notifications)
            key: Clé du paramètre
            default: Valeur par défaut si le paramètre n'existe pas

        Returns:
            Valeur du paramètre ou valeur par défaut
        """
        section_dict = getattr(self, section, {})
        return section_dict.get(key, default)

    def set_value(self, section: str, key: str, value: Any) -> None:
        """
        Définit une valeur de paramètre

        Args:
            section: Section du paramètre (ui, export, notifications)
            key: Clé du paramètre
            value: Nouvelle valeur
        """
        if hasattr(self, section):
            section_dict = getattr(self, section)
            section_dict[key] = value
        else:
            raise ValueError(f"Section de paramètres inconnue: {section}")

    def to_dict(self) -> Dict[str, Dict[str, Any]]:
        """
        Convertit les paramètres en dictionnaire

        Returns:
            Dictionnaire des paramètres
        """
        return {
            "ui": self.ui,
            "export": self.export,
            "notifications": self.notifications,
        }


# Instance singleton des paramètres
settings = Settings()