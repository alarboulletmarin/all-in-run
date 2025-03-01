"""
Modèle pour représenter un plan d'entraînement complet.
"""
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Dict, List, Any, Optional, Tuple
import json
from collections import defaultdict

from .user_data import UserData
from .session import Session, TrainingPhase, SessionType


@dataclass
class TrainingPlan:
    """
    Représente un plan d'entraînement complet.

    Attributes:
        user_data: Données utilisateur ayant servi à générer le plan
        sessions: Dictionnaire des séances indexées par date
        phase_dates: Dictionnaire des plages de dates pour chaque phase
        weekly_volumes: Dictionnaire des volumes par semaine
        version: Version du format de données du plan
    """
    user_data: UserData
    sessions: Dict[date, Session] = field(default_factory=dict)
    phase_dates: Dict[TrainingPhase, List[date]] = field(default_factory=dict)
    weekly_volumes: Dict[int, float] = field(default_factory=dict)
    version: str = "1.0.0"

    def add_session(self, session: Session) -> None:
        """Ajoute une séance au plan"""
        self.sessions[session.session_date] = session

    def get_session(self, session_date: date) -> Optional[Session]:
        """Récupère une séance par sa date"""
        return self.sessions.get(session_date)

    def get_sessions_by_week(self) -> Dict[int, List[Session]]:
        """
        Regroupe les séances par semaine

        Returns:
            Dictionnaire avec la semaine (0-indexed) comme clé et une liste de séances comme valeur
        """
        sessions_by_week = defaultdict(list)

        for session_date, session in self.sessions.items():
            # Calculer le numéro de semaine (0-indexed)
            week_num = (session_date - self.user_data.start_date).days // 7
            sessions_by_week[week_num].append(session)

        return dict(sessions_by_week)

    def get_sessions_by_type(self) -> Dict[SessionType, List[Session]]:
        """
        Regroupe les séances par type

        Returns:
            Dictionnaire avec le type de séance comme clé et une liste de séances comme valeur
        """
        sessions_by_type = defaultdict(list)

        for session in self.sessions.values():
            sessions_by_type[session.session_type].append(session)

        return dict(sessions_by_type)

    def get_sessions_by_phase(self) -> Dict[TrainingPhase, List[Session]]:
        """
        Regroupe les séances par phase d'entraînement

        Returns:
            Dictionnaire avec la phase comme clé et une liste de séances comme valeur
        """
        sessions_by_phase = defaultdict(list)

        for session in self.sessions.values():
            sessions_by_phase[session.phase].append(session)

        return dict(sessions_by_phase)

    def get_weekly_volume(self, week_num: int) -> float:
        """
        Calcule le volume total d'une semaine spécifique

        Args:
            week_num: Numéro de la semaine (0-indexed)

        Returns:
            Volume total en km, arrondi au dixième
        """
        if week_num in self.weekly_volumes:
            return self.weekly_volumes[week_num]

        total = 0.0
        sessions_by_week = self.get_sessions_by_week()

        if week_num in sessions_by_week:
            for session in sessions_by_week[week_num]:
                total += session.total_distance

        # Arrondir au dixième
        return round(total, 1)

    def get_weekly_duration(self, week_num: int) -> timedelta:
        """
        Calcule la durée totale d'une semaine spécifique

        Args:
            week_num: Numéro de la semaine (0-indexed)

        Returns:
            Durée totale en timedelta
        """
        total_seconds = 0
        sessions_by_week = self.get_sessions_by_week()

        if week_num in sessions_by_week:
            for session in sessions_by_week[week_num]:
                total_seconds += session.total_duration.total_seconds()

        return timedelta(seconds=total_seconds)

    def get_total_volume(self) -> float:
        """
        Calcule le volume total du plan

        Returns:
            Volume total en km, arrondi au dixième
        """
        total = sum(session.total_distance for session in self.sessions.values())
        return round(total, 1)

    def get_total_duration(self) -> timedelta:
        """
        Calcule la durée totale du plan

        Returns:
            Durée totale en timedelta
        """
        total_seconds = sum(session.total_duration.total_seconds() for session in self.sessions.values())
        return timedelta(seconds=total_seconds)

    def get_phase_for_date(self, date_to_check: date) -> Optional[TrainingPhase]:
        """
        Détermine la phase d'entraînement pour une date donnée

        Args:
            date_to_check: Date à vérifier

        Returns:
            Phase d'entraînement ou None si la date n'est pas dans le plan
        """
        for phase, dates in self.phase_dates.items():
            if date_to_check in dates:
                return phase
        return None

    def get_week_number(self, date_to_check: date) -> Optional[int]:
        """
        Détermine le numéro de semaine pour une date donnée

        Args:
            date_to_check: Date à vérifier

        Returns:
            Numéro de semaine (0-indexed) ou None si la date n'est pas dans le plan
        """
        if date_to_check < self.user_data.start_date or date_to_check > self.user_data.main_race.race_date:
            return None

        return (date_to_check - self.user_data.start_date).days // 7

    def get_week_dates(self, week_num: int) -> Tuple[date, date]:
        """
        Retourne les dates de début et de fin d'une semaine

        Args:
            week_num: Numéro de la semaine (0-indexed)

        Returns:
            Tuple avec la date de début (lundi) et la date de fin (dimanche) de la semaine
        """
        start = self.user_data.start_date + timedelta(days=week_num * 7)
        end = start + timedelta(days=6)
        return start, end

    def get_phase_stats(self) -> Dict[TrainingPhase, Dict[str, Any]]:
        """
        Calcule les statistiques pour chaque phase

        Returns:
            Dictionnaire avec les statistiques par phase
        """
        stats = {}

        for phase in TrainingPhase:
            phase_sessions = [s for s in self.sessions.values() if s.phase == phase]

            if not phase_sessions:
                continue

            # Dates de début et fin de la phase
            phase_dates = sorted([s.session_date for s in phase_sessions])
            start_date = min(phase_dates)
            end_date = max(phase_dates)

            # Calcul des statistiques
            total_volume = sum(s.total_distance for s in phase_sessions)
            total_seconds = sum(s.total_duration.total_seconds() for s in phase_sessions)

            # Nombre de semaines
            num_weeks = (end_date - start_date).days // 7 + 1

            # Répartition des types de séances
            session_types = {}
            for type_enum in SessionType:
                count = len([s for s in phase_sessions if s.session_type == type_enum])
                if count > 0:
                    session_types[type_enum.value] = count

            stats[phase] = {
                "start_date": start_date,
                "end_date": end_date,
                "num_weeks": num_weeks,
                "total_volume": round(total_volume, 1),
                "total_duration": timedelta(seconds=total_seconds),
                "avg_weekly_volume": round(total_volume / num_weeks, 1),
                "session_types": session_types
            }

        return stats

    def to_dict(self) -> Dict[str, Any]:
        """
        Convertit le plan en dictionnaire pour sérialisation JSON

        Returns:
            Dictionnaire représentant le plan
        """
        # Conversion des sessions
        sessions_dict = {
            session_date.isoformat(): session.to_dict()
            for session_date, session in self.sessions.items()
        }

        # Conversion des phases
        phase_dates_dict = {
            phase.value: [d.isoformat() for d in dates]
            for phase, dates in self.phase_dates.items()
        }

        return {
            "version": self.version,
            "user_data": self.user_data.to_dict(),
            "sessions": sessions_dict,
            "phase_dates": phase_dates_dict,
            "weekly_volumes": {str(week): volume for week, volume in self.weekly_volumes.items()}
        }

    def to_json(self) -> str:
        """
        Serialise le plan au format JSON

        Returns:
            Chaîne JSON
        """
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TrainingPlan':
        """
        Crée un objet TrainingPlan à partir d'un dictionnaire

        Args:
            data: Dictionnaire représentant le plan

        Returns:
            Objet TrainingPlan
        """
        # Conversion des données utilisateur
        user_data = UserData.from_dict(data["user_data"])

        # Création du plan
        plan = cls(
            user_data=user_data,
            version=data.get("version", "1.0.0")
        )

        # Conversion des sessions
        for session_date_str, session_data in data.get("sessions", {}).items():
            session_date = date.fromisoformat(session_date_str)
            session = Session.from_dict(session_data)
            plan.sessions[session_date] = session

        # Conversion des phases
        for phase_str, dates_str in data.get("phase_dates", {}).items():
            phase = TrainingPhase(phase_str)
            plan.phase_dates[phase] = [date.fromisoformat(d) for d in dates_str]

        # Conversion des volumes hebdomadaires
        for week_str, volume in data.get("weekly_volumes", {}).items():
            plan.weekly_volumes[int(week_str)] = float(volume)

        return plan

    @classmethod
    def from_json(cls, json_str: str) -> 'TrainingPlan':
        """
        Crée un objet TrainingPlan à partir d'une chaîne JSON

        Args:
            json_str: Chaîne JSON représentant le plan

        Returns:
            Objet TrainingPlan
        """
        data = json.loads(json_str)
        return cls.from_dict(data)

    def adjust_to_current_date(self, current_date: date) -> 'TrainingPlan':
        """
        Ajuste le plan à la date courante en considérant toutes les séances passées comme complétées

        Args:
            current_date: Date courante

        Returns:
            Plan ajusté (self modifié)
        """
        # Vérifier si la date est postérieure à la course principale
        if current_date > self.user_data.main_race.race_date:
            raise ValueError("La date courante est postérieure à la date de la course principale")

        # Vérifier si la date est antérieure au début du plan
        if current_date < self.user_data.start_date:
            return self  # Aucun ajustement nécessaire

        # Si la date est entre le début du plan et la course, on conserve seulement
        # les séances à venir (>= current_date)
        return self  # Dans cette implémentation de base, on ne modifie rien