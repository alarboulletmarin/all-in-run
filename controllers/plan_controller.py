from datetime import date
from typing import Dict, Any, Optional, Union, BinaryIO, List

from models.plan import TrainingPlan
from models.user_data import UserData
from services.export_service import ExportService
from services.import_service import ImportService
from services.plan_generator import PlanGenerator
from utils.storage import storage_manager


class PlanController:
    """Contrôleur responsable de la gestion, génération, manipulation et export des plans d'entraînement"""

    def __init__(self):
        self.plan_generator = PlanGenerator()
        self.export_service = ExportService()
        self.import_service = ImportService()
        self.current_plan: Optional[TrainingPlan] = None

    def generate_plan(self, user_data: UserData) -> TrainingPlan:
        """
        Génère un plan d'entraînement personnalisé à partir des données utilisateur

        Args:
            user_data: Données utilisateur incluant objectifs, profil et contraintes

        Returns:
            Un plan d'entraînement complet adapté aux besoins de l'utilisateur
        """
        # Vérifier si les données ont changé par rapport au plan existant
        force_regenerate = True
        if self.current_plan and hasattr(self.current_plan, 'user_data'):
            force_regenerate = not self._compare_user_data(self.current_plan.user_data, user_data)
        
        # Générer un nouveau plan d'entraînement
        self.current_plan = self.plan_generator.generate_plan(user_data)

        # Persistance des données
        self._save_current_plan()

        return self.current_plan
        
    def _compare_user_data(self, old_data: UserData, new_data: UserData) -> bool:
        """
        Compare deux objets UserData pour détecter des changements significatifs
        
        Args:
            old_data: Données utilisateur précédentes
            new_data: Nouvelles données utilisateur
            
        Returns:
            True si les données sont essentiellement identiques, False si des changements
            nécessitent une régénération du plan
        """
        # Comparaison des dates et paramètres principaux
        if old_data.start_date != new_data.start_date:
            return False
        if old_data.main_race.race_date != new_data.main_race.race_date:
            return False
        if old_data.main_race.race_type != new_data.main_race.race_type:
            return False
        if old_data.sessions_per_week != new_data.sessions_per_week:
            return False
        if old_data.min_volume != new_data.min_volume:
            return False
        if old_data.max_volume != new_data.max_volume:
            return False
        
        # Comparaison des allures de référence
        if old_data.pace_5k != new_data.pace_5k:
            return False
        if old_data.pace_10k != new_data.pace_10k:
            return False
        if old_data.pace_half_marathon != new_data.pace_half_marathon:
            return False
        if old_data.pace_marathon != new_data.pace_marathon:
            return False
            
        # Vérification des courses intermédiaires
        if len(old_data.intermediate_races) != len(new_data.intermediate_races):
            return False
        
        return True

    def load_plan(self) -> Optional[TrainingPlan]:
        """
        Charge le plan d'entraînement depuis le stockage persistant

        Returns:
            Le plan d'entraînement stocké ou None si aucun plan n'existe
        """
        self.current_plan = storage_manager.load_plan()
        return self.current_plan

    def get_current_plan(self) -> Optional[TrainingPlan]:
        """
        Récupère le plan courant ou le charge depuis le stockage si nécessaire

        Returns:
            Le plan d'entraînement courant ou None si aucun plan n'est disponible
        """
        if self.current_plan is None:
            self.current_plan = self.load_plan()

        return self.current_plan

    def export_to_ics(self, lang: str = "fr", options: dict = None) -> Optional[bytes]:
        """
        Exporte le plan courant au format iCalendar (ICS) pour intégration avec les agendas

        Args:
            lang: Code de langue pour la localisation des descriptions
            options: Options de personnalisation de l'export

        Returns:
            Contenu binaire du fichier ICS ou None si aucun plan n'est disponible
        """
        if self.current_plan is None:
            return None

        return self.export_service.export_to_ics(self.current_plan, lang, options)

    def export_to_pdf(self, lang: str = "fr", options: dict = None) -> Optional[bytes]:
        """
        Exporte le plan courant au format PDF pour impression ou partage

        Args:
            lang: Code de langue pour la localisation du contenu
            options: Options de personnalisation du PDF:
                - include_charts: Affichage des graphiques d'analyse (bool)
                - include_details: Inclusion des détails d'entraînement (bool)
                - paper_size: Format du papier ("A4", "Letter", "Legal")
                - orientation: Orientation de la page ("portrait", "landscape")

        Returns:
            Contenu binaire du PDF ou None si aucun plan n'est disponible
        """
        if self.current_plan is None:
            return None

        return self.export_service.export_to_pdf(self.current_plan, lang, options)

    def export_to_json(self) -> Optional[str]:
        """
        Exporte le plan courant au format JSON pour sauvegarde ou partage

        Returns:
            Chaîne JSON représentant le plan ou None si aucun plan n'est disponible
        """
        if self.current_plan is None:
            return None

        return self.export_service.export_to_json(self.current_plan)

    def export_to_tcx(self, lang: str = "fr") -> Optional[bytes]:
        """
        Exporte le plan courant au format TCX pour importation dans les appareils Garmin

        Args:
            lang: Code de langue pour la localisation des descriptions d'entraînement

        Returns:
            Contenu binaire du fichier TCX ou None si aucun plan n'est disponible
        """
        if self.current_plan is None:
            return None

        return self.export_service.export_to_tcx(self.current_plan, lang)

    def import_from_json(self, json_data: Union[str, BinaryIO]) -> Optional[TrainingPlan]:
        """
        Importe un plan d'entraînement depuis des données JSON

        Args:
            json_data: Données JSON sous forme de chaîne ou de fichier ouvert

        Returns:
            Le plan importé ou None en cas d'échec de l'importation
        """
        try:
            self.current_plan = self.import_service.import_from_json(json_data)
            self._save_current_plan()
            return self.current_plan
        except Exception as e:
            print(f"Erreur lors de l'importation du plan: {e}")
            return None

    def adjust_to_current_date(self, current_date: Optional[date] = None) -> Optional[TrainingPlan]:
        """
        Ajuste le plan d'entraînement en fonction de la date actuelle
        Utile pour adapter un plan existant si l'utilisateur a manqué des séances
        ou souhaite commencer le plan à une nouvelle date

        Args:
            current_date: Date de référence pour l'ajustement (date du jour par défaut)

        Returns:
            Plan ajusté ou None si l'ajustement a échoué ou si aucun plan n'est chargé
        """
        if self.current_plan is None:
            return None

        if current_date is None:
            current_date = date.today()

        try:
            adjusted_plan = self.plan_generator.adjust_plan(self.current_plan, current_date)
            self.current_plan = adjusted_plan
            self._save_current_plan()
            return self.current_plan
        except Exception as e:
            print(f"Erreur lors de l'ajustement du plan: {e}")
            return None

    def get_plan_summary(self) -> Dict[str, Any]:
        """
        Produit un résumé synthétique du plan d'entraînement actuel
        Utile pour l'affichage dans les tableaux de bord ou écrans récapitulatifs

        Returns:
            Dictionnaire structuré contenant les métriques clés du plan
        """
        if self.current_plan is None:
            return {}

        # Informations générales
        summary = {
            "start_date": self.current_plan.user_data.start_date,
            "race_date": self.current_plan.user_data.main_race.race_date,
            "race_type": self.current_plan.user_data.main_race.race_type.value,
            "total_weeks": self.current_plan.user_data.total_weeks,
            "total_volume": self.current_plan.get_total_volume(),
            "total_duration": self.current_plan.get_total_duration(),
            "sessions_per_week": self.current_plan.user_data.sessions_per_week
        }

        # Informations sur les phases
        phase_stats = self.current_plan.get_phase_stats()
        summary["phases"] = {
            phase.value: {
                "start_date": stats["start_date"],
                "end_date": stats["end_date"],
                "num_weeks": stats["num_weeks"],
                "total_volume": stats["total_volume"],
                "total_duration": stats["total_duration"]
            }
            for phase, stats in phase_stats.items()
        }

        # Volumes hebdomadaires
        summary["weekly_volumes"] = {
            str(week): volume
            for week, volume in self.current_plan.weekly_volumes.items()
        }

        return summary

    def get_week_sessions(self, week_num: int) -> List[Dict[str, Any]]:
        """
        Récupère les détails des séances d'une semaine spécifique du plan

        Args:
            week_num: Numéro de la semaine (0 pour la première semaine)

        Returns:
            Liste des séances d'entraînement de la semaine avec leurs détails
        """
        if self.current_plan is None:
            return []

        sessions_by_week = self.current_plan.get_sessions_by_week()
        if week_num not in sessions_by_week:
            return []

        # Trier les séances par jour de la semaine
        sorted_sessions = sorted(sessions_by_week[week_num], key=lambda s: s.session_date.weekday())

        # Convertir les séances en dictionnaires
        session_dicts = []
        for session in sorted_sessions:
            session_dict = {
                "date": session.session_date,
                "day_of_week": session.session_date.weekday(),
                "type": session.session_type.value,
                "phase": session.phase.value,
                "distance": session.total_distance,
                "duration": session.total_duration,
                "description": session.description,
                "is_intermediate_race": session.is_intermediate_race
            }

            if session.blocks:
                session_dict["blocks"] = [
                    {
                        "distance": block.distance,
                        "pace": block.pace,
                        "duration": block.duration,
                        "description": block.description
                    }
                    for block in session.blocks
                ]

            session_dicts.append(session_dict)

        return session_dicts

    def get_week_summary(self, week_num: int) -> Dict[str, Any]:
        """
        Génère un résumé des métriques d'une semaine spécifique du plan

        Args:
            week_num: Numéro de la semaine (0 pour la première semaine)

        Returns:
            Dictionnaire contenant les statistiques et informations clés de la semaine
        """
        if self.current_plan is None:
            return {}

        # Obtenir les dates de début et de fin de la semaine
        start_date, end_date = self.current_plan.get_week_dates(week_num)

        # Calculer le volume et la durée de la semaine
        volume = self.current_plan.get_weekly_volume(week_num)
        duration = self.current_plan.get_weekly_duration(week_num)

        # Déterminer la phase de la semaine
        phase = None
        for day in range(7):
            day_date = start_date + date.resolution * day
            day_phase = self.current_plan.get_phase_for_date(day_date)
            if day_phase:
                phase = day_phase
                break

        # Compter les types de séances
        sessions = self.get_week_sessions(week_num)
        session_types = {}
        for session in sessions:
            session_type = session["type"]
            session_types[session_type] = session_types.get(session_type, 0) + 1

        return {
            "week_num": week_num,
            "start_date": start_date,
            "end_date": end_date,
            "volume": volume,
            "duration": duration,
            "phase": phase.value if phase else None,
            "session_types": session_types
        }

    def _save_current_plan(self) -> None:
        """
        Sauvegarde le plan courant dans le stockage persistant
        Cette méthode privée est appelée automatiquement après chaque modification du plan
        """
        if self.current_plan:
            storage_manager.save_plan(self.current_plan)