import os
from typing import Dict, Any
import json


class Settings:
    """Gestionnaire centralisé de configuration de l'application"""

    def __init__(self, config_file: str = None):
        """
        Initialise les paramètres avec des valeurs par défaut et charge une configuration externe si spécifiée
        
        Args:
            config_file: Chemin vers un fichier de configuration JSON (optionnel)
        """
        # Configuration de l'interface utilisateur
        self.ui = {
            "theme": "light",             # Thème de l'application (light/dark)
            "show_tips": True,            # Affichage des conseils utilisateur
            "display_mode": "calendar",   # Mode d'affichage du plan (calendar/list)
        }

        # Configuration des exports
        self.export = {
            "ics_calendar_name": "All-in-Run",  # Nom du calendrier pour export iCalendar
            "pdf_include_charts": True,         # Inclusion des graphiques dans l'export PDF
            "pdf_include_stats": True,          # Inclusion des statistiques dans l'export PDF
        }

        # Configuration des notifications
        self.notifications = {
            "enabled": False,             # Activation du système de notifications
            "reminder_days": 1,           # Jours d'anticipation pour les rappels
        }

        # Charge la configuration depuis un fichier si spécifié et existant
        if config_file and os.path.exists(config_file):
            self.load_from_file(config_file)

    def load_from_file(self, config_file: str) -> None:
        """
        Charge les paramètres depuis un fichier JSON et met à jour la configuration
        
        Args:
            config_file: Chemin vers le fichier de configuration
        """
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)

            # Mise à jour sélective des sections de configuration
            if "ui" in config_data:
                self.ui.update(config_data["ui"])
            if "export" in config_data:
                self.export.update(config_data["export"])
            if "notifications" in config_data:
                self.notifications.update(config_data["notifications"])

        except (json.JSONDecodeError, IOError) as e:
            print(f"Erreur lors du chargement des paramètres: {e}")

    def save_to_file(self, config_file: str) -> None:
        """
        Sauvegarde la configuration actuelle dans un fichier JSON
        
        Args:
            config_file: Chemin vers le fichier de destination
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
        Récupère une valeur de paramètre avec gestion des valeurs par défaut
        
        Args:
            section: Section du paramètre (ui, export, notifications)
            key: Identifiant du paramètre
            default: Valeur par défaut retournée si le paramètre n'est pas trouvé
            
        Returns:
            La valeur du paramètre ou la valeur par défaut
        """
        section_dict = getattr(self, section, {})
        return section_dict.get(key, default)

    def set_value(self, section: str, key: str, value: Any) -> None:
        """
        Définit ou met à jour une valeur de paramètre
        
        Args:
            section: Section du paramètre (ui, export, notifications)
            key: Identifiant du paramètre
            value: Nouvelle valeur à définir
            
        Raises:
            ValueError: Si la section spécifiée n'existe pas
        """
        if hasattr(self, section):
            section_dict = getattr(self, section)
            section_dict[key] = value
        else:
            raise ValueError(f"Section de paramètres inconnue: {section}")

    def to_dict(self) -> Dict[str, Dict[str, Any]]:
        """
        Exporte la configuration complète sous forme de dictionnaire
        
        Returns:
            Dictionnaire complet des paramètres organisés par section
        """
        return {
            "ui": self.ui,
            "export": self.export,
            "notifications": self.notifications,
        }


# Instance globale des paramètres pour l'application
settings = Settings()