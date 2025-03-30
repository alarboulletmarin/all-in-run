from datetime import date
from typing import Dict

from models.plan import TrainingPlan
from models.user_data import UserData
from models.session import Session, TrainingPhase
from .phase_calculator import PhaseCalculator
from .volume_calculator import VolumeCalculator
from .session_distributor import SessionDistributor


class PlanGenerator:
    """Génère un plan d'entraînement complet"""

    def __init__(self):
        self.phase_calculator = PhaseCalculator()
        self.volume_calculator = VolumeCalculator()
        self.session_distributor = SessionDistributor()

    def generate_plan(self, user_data: UserData) -> TrainingPlan:
        """
        Génère un plan d'entraînement complet

        Args:
            user_data: Données utilisateur

        Returns:
            Plan d'entraînement complet
        """
        # 1. Calculer les phases
        phases = self.phase_calculator.calculate_phases(
            user_data.start_date,
            user_data.main_race.race_date
        )

        # 2. Calculer les volumes hebdomadaires
        weekly_volumes = self.volume_calculator.calculate_volumes(
            user_data.min_volume,
            user_data.max_volume,
            phases,
            user_data.intermediate_races
        )

        # 3. Calculer l'allure d'endurance fondamentale
        ef_pace = user_data.calculate_ef_pace()

        # 4. Distribuer les séances
        sessions = self.session_distributor.distribute_sessions(
            user_data.start_date,
            phases,
            weekly_volumes,
            user_data.sessions_per_week,
            ef_pace,
            user_data.specific_pace,
            user_data.intermediate_races
        )

        # 5. Ajouter la course principale
        race_session = Session.create_race_session(
            session_date=user_data.main_race.race_date,
            phase=TrainingPhase.TAPER,
            race_distance=user_data.main_race.get_standard_distance,
            race_pace=user_data.specific_pace,
            description=f"Course principale: {user_data.main_race.race_type.value}"
        )

        sessions[user_data.main_race.race_date] = race_session

        # 6. Créer le plan complet
        plan = TrainingPlan(
            user_data=user_data,
            sessions=sessions,
            phase_dates=phases,
            weekly_volumes=weekly_volumes
        )

        return plan

    def adjust_plan(self, plan: TrainingPlan, current_date: date) -> TrainingPlan:
        """
        Ajuste un plan existant à la date courante

        Args:
            plan: Plan d'entraînement à ajuster
            current_date: Date courante

        Returns:
            Plan ajusté
        """
        # Vérifier si la date est postérieure à la course principale
        if current_date > plan.user_data.main_race.race_date:
            raise ValueError("La date courante est postérieure à la date de la course principale")

        # Si la date est antérieure au début du plan, retourner le plan tel quel
        if current_date < plan.user_data.start_date:
            return plan

        # Liste des séances à conserver (toutes les séances à venir)
        future_sessions = {
            session_date: session
            for session_date, session in plan.sessions.items()
            if session_date >= current_date
        }

        # Créer un nouveau plan avec les séances ajustées
        adjusted_plan = TrainingPlan(
            user_data=plan.user_data,
            sessions=future_sessions,
            phase_dates=plan.phase_dates,
            weekly_volumes=plan.weekly_volumes,
            version=plan.version
        )

        return adjusted_plan

    def simulate_plan(self, user_data: UserData, simulation_params: Dict) -> TrainingPlan:
        """
        Génère un plan simulé avec des paramètres modifiés

        Args:
            user_data: Données utilisateur de base
            simulation_params: Paramètres à modifier pour la simulation

        Returns:
            Plan d'entraînement simulé
        """
        # Créer une copie modifiée des données utilisateur
        simulated_data = UserData(
            start_date=simulation_params.get("start_date", user_data.start_date),
            main_race=simulation_params.get("main_race", user_data.main_race),
            pace_5k=simulation_params.get("pace_5k", user_data.pace_5k),
            pace_10k=simulation_params.get("pace_10k", user_data.pace_10k),
            pace_half_marathon=simulation_params.get("pace_half_marathon", user_data.pace_half_marathon),
            pace_marathon=simulation_params.get("pace_marathon", user_data.pace_marathon),
            sessions_per_week=simulation_params.get("sessions_per_week", user_data.sessions_per_week),
            min_volume=simulation_params.get("min_volume", user_data.min_volume),
            max_volume=simulation_params.get("max_volume", user_data.max_volume),
            intermediate_races=simulation_params.get("intermediate_races", user_data.intermediate_races)
        )

        # Générer le plan simulé
        return self.generate_plan(simulated_data)