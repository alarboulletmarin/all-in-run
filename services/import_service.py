"""
Service d'importation du plan d'entraînement.
"""
import json
from datetime import date
from typing import Dict, Any, Optional, Union, TextIO, BinaryIO

from models.plan import TrainingPlan


class ImportService:
    """Service d'importation du plan d'entraînement"""

    def import_from_json(self, json_data: Union[str, TextIO]) -> TrainingPlan:
        """
        Importe un plan d'entraînement à partir de données JSON

        Args:
            json_data: Chaîne JSON ou fichier JSON ouvert en lecture

        Returns:
            Plan d'entraînement importé
        """
        # Convertir les données JSON en dictionnaire
        if isinstance(json_data, str):
            data = json.loads(json_data)
        else:
            data = json.load(json_data)

        # Créer le plan d'entraînement à partir du dictionnaire
        return TrainingPlan.from_dict(data)

    def adjust_plan_to_current_date(self, plan: TrainingPlan, current_date: Optional[date] = None) -> TrainingPlan:
        """
        Ajuste un plan d'entraînement à la date courante

        Args:
            plan: Plan d'entraînement à ajuster
            current_date: Date courante (si None, utilise la date du jour)

        Returns:
            Plan d'entraînement ajusté
        """
        if current_date is None:
            current_date = date.today()

        # Vérifier si la date est postérieure à la course
        if current_date > plan.user_data.main_race.race_date:
            raise ValueError("La date courante est postérieure à la date de la course principale")

        # Si la date est antérieure au début du plan, retourner le plan tel quel
        if current_date < plan.user_data.start_date:
            return plan

        # Créer un nouveau plan avec seulement les séances futures
        future_sessions = {
            session_date: session
            for session_date, session in plan.sessions.items()
            if session_date >= current_date
        }

        adjusted_plan = TrainingPlan(
            user_data=plan.user_data,
            sessions=future_sessions,
            phase_dates=plan.phase_dates,
            weekly_volumes=plan.weekly_volumes,
            version=plan.version
        )

        return adjusted_plan