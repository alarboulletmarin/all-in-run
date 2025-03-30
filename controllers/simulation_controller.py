from datetime import timedelta
from typing import Dict, Any, List, Optional

from models.plan import TrainingPlan
from models.user_data import UserData
from models.course import Course
from services.plan_generator import PlanGenerator


class SimulationController:
    """
    Contrôleur responsable de la simulation de plans d'entraînement alternatifs.
    Permet de comparer différents scénarios et ajustements de paramètres.
    """

    def __init__(self):
        self.plan_generator = PlanGenerator()
        self.current_simulation: Optional[TrainingPlan] = None
        self.original_user_data: Optional[UserData] = None

    def simulate_plan(self, user_data: UserData,
                      simulation_params: Dict[str, Any]) -> TrainingPlan:
        """
        Génère un plan d'entraînement simulé à partir de paramètres modifiés.

        Args:
            user_data: Données utilisateur de référence
            simulation_params: Paramètres à modifier pour cette simulation

        Returns:
            Plan d'entraînement simulé avec les paramètres modifiés
        """
        # Conserver les données originales pour comparaison ultérieure
        self.original_user_data = user_data

        # Appliquer les modifications demandées aux données utilisateur
        modified_user_data = self._apply_simulation_params(user_data, simulation_params)

        # Générer le plan avec les paramètres modifiés
        self.current_simulation = self.plan_generator.generate_plan(modified_user_data)

        return self.current_simulation

    def compare_plans(self, original_plan: TrainingPlan,
                      simulated_plan: TrainingPlan) -> Dict[str, Any]:
        """
        Analyse et compare deux plans d'entraînement en détail.

        Args:
            original_plan: Plan d'entraînement de référence
            simulated_plan: Plan d'entraînement simulé à comparer

        Returns:
            Analyse comparative détaillée des deux plans (volumes, durées, types de séances, etc.)
        """
        comparison = {}

        # Analyse comparative des volumes totaux
        original_volume = original_plan.get_total_volume()
        simulated_volume = simulated_plan.get_total_volume()
        volume_diff = simulated_volume - original_volume
        volume_diff_percent = (volume_diff / original_volume) * 100 if original_volume else 0

        comparison["volume"] = {
            "original": original_volume,
            "simulated": simulated_volume,
            "difference": volume_diff,
            "difference_percent": volume_diff_percent
        }

        # Analyse comparative des durées d'entraînement
        original_duration = original_plan.get_total_duration()
        simulated_duration = simulated_plan.get_total_duration()
        duration_diff = simulated_duration - original_duration
        duration_diff_seconds = duration_diff.total_seconds()

        comparison["duration"] = {
            "original": original_duration,
            "simulated": simulated_duration,
            "difference": duration_diff
        }

        # Analyse comparative de la distribution des types de séances
        original_types = self._count_session_types(original_plan)
        simulated_types = self._count_session_types(simulated_plan)

        comparison["session_types"] = {
            "original": original_types,
            "simulated": simulated_types
        }

        # Analyse comparative des volumes hebdomadaires
        comparison["weekly_volumes"] = {
            "original": original_plan.weekly_volumes,
            "simulated": simulated_plan.weekly_volumes
        }

        # Analyse comparative des phases d'entraînement
        original_phase_stats = original_plan.get_phase_stats()
        simulated_phase_stats = simulated_plan.get_phase_stats()

        comparison["phases"] = {
            "original": {
                phase.value: {
                    "num_weeks": stats["num_weeks"],
                    "total_volume": stats["total_volume"]
                }
                for phase, stats in original_phase_stats.items()
            },
            "simulated": {
                phase.value: {
                    "num_weeks": stats["num_weeks"],
                    "total_volume": stats["total_volume"]
                }
                for phase, stats in simulated_phase_stats.items()
            }
        }

        return comparison

    def get_simulation_scenarios(self, user_data: UserData) -> List[Dict[str, Any]]:
        """
        Génère une liste de scénarios de simulation prédéfinis adaptés au profil de l'utilisateur.

        Args:
            user_data: Données utilisateur pour lesquelles générer des scénarios

        Returns:
            Liste de scénarios de simulation avec leurs paramètres associés
        """
        scenarios = []

        # Scénario: Augmentation de la fréquence d'entraînement
        if user_data.sessions_per_week < 7:
            scenarios.append({
                "name": f"Augmenter à {user_data.sessions_per_week + 1} séances par semaine",
                "description": "Plus de séances hebdomadaires pour une meilleure répartition de l'effort",
                "params": {
                    "sessions_per_week": user_data.sessions_per_week + 1
                }
            })

        # Scénario: Diminution de la fréquence d'entraînement
        if user_data.sessions_per_week > 3:
            scenarios.append({
                "name": f"Réduire à {user_data.sessions_per_week - 1} séances par semaine",
                "description": "Moins de séances mais plus longues pour un meilleur équilibre vie/entraînement",
                "params": {
                    "sessions_per_week": user_data.sessions_per_week - 1
                }
            })

        # Scénario: Augmentation du volume hebdomadaire
        max_volume_increase = user_data.max_volume * 1.2
        min_volume_increase = user_data.min_volume * 1.2

        scenarios.append({
            "name": "Augmenter le volume (+20%)",
            "description": "Plus de kilomètres pour une meilleure endurance",
            "params": {
                "max_volume": round(max_volume_increase, 1),
                "min_volume": round(min_volume_increase, 1)
            }
        })

        # Scénario: Diminution du volume hebdomadaire
        max_volume_decrease = user_data.max_volume * 0.8
        min_volume_decrease = user_data.min_volume * 0.8

        scenarios.append({
            "name": "Diminuer le volume (-20%)",
            "description": "Moins de kilomètres pour réduire le risque de blessure",
            "params": {
                "max_volume": round(max_volume_decrease, 1),
                "min_volume": round(min_volume_decrease, 1)
            }
        })

        # Scénario: Démarrage du plan plus tardif
        current_weeks = (user_data.main_race.race_date - user_data.start_date).days // 7

        if current_weeks > 16:
            later_start = user_data.start_date + timedelta(days=28)
            scenarios.append({
                "name": "Commencer 4 semaines plus tard",
                "description": "Raccourcir la période de préparation",
                "params": {
                    "start_date": later_start
                }
            })

        # Scénario: Allures plus rapides (plus intense)
        faster_paces = {
            "pace_5k": user_data.pace_5k - timedelta(seconds=10),
            "pace_10k": user_data.pace_10k - timedelta(seconds=8),
            "pace_half_marathon": user_data.pace_half_marathon - timedelta(seconds=5),
            "pace_marathon": user_data.pace_marathon - timedelta(seconds=3)
        }

        scenarios.append({
            "name": "Allures plus rapides",
            "description": "Entraînement plus intensif pour atteindre un objectif ambitieux",
            "params": faster_paces
        })

        # Scénario: Allures plus lentes (moins intense)
        slower_paces = {
            "pace_5k": user_data.pace_5k + timedelta(seconds=10),
            "pace_10k": user_data.pace_10k + timedelta(seconds=8),
            "pace_half_marathon": user_data.pace_half_marathon + timedelta(seconds=5),
            "pace_marathon": user_data.pace_marathon + timedelta(seconds=3)
        }

        scenarios.append({
            "name": "Allures plus lentes",
            "description": "Entraînement moins intensif pour un confort optimal",
            "params": slower_paces
        })

        return scenarios

    def get_current_simulation(self) -> Optional[TrainingPlan]:
        """
        Récupère la simulation de plan en cours.

        Returns:
            Le plan d'entraînement simulé ou None si aucune simulation n'existe
        """
        return self.current_simulation

    def _apply_simulation_params(self, user_data: UserData,
                                 simulation_params: Dict[str, Any]) -> UserData:
        """
        Applique les paramètres de simulation aux données utilisateur pour créer un profil modifié.

        Args:
            user_data: Données utilisateur originales
            simulation_params: Paramètres de simulation à appliquer

        Returns:
            Données utilisateur modifiées selon les paramètres spécifiés
        """
        # Traitement de la course principale
        main_race_params = simulation_params.get("main_race", {})
        main_race = Course(
            race_date=main_race_params.get("race_date", user_data.main_race.race_date),
            race_type=main_race_params.get("race_type", user_data.main_race.race_type),
            distance=main_race_params.get("distance", user_data.main_race.distance),
            target_time=main_race_params.get("target_time", user_data.main_race.target_time),
            target_pace=main_race_params.get("target_pace", user_data.main_race.target_pace),
            is_main_race=True
        )

        # Traitement des courses intermédiaires (modification ou ajout)
        intermediate_races = []
        for race in user_data.intermediate_races:
            modified = False
            for race_params in simulation_params.get("intermediate_races", []):
                if race_params.get("race_date") == race.race_date:
                    new_race = Course(
                        race_date=race_params.get("race_date", race.race_date),
                        race_type=race_params.get("race_type", race.race_type),
                        distance=race_params.get("distance", race.distance),
                        target_pace=race_params.get("target_pace", race.target_pace),
                        is_main_race=False
                    )
                    intermediate_races.append(new_race)
                    modified = True
                    break

            if not modified:
                intermediate_races.append(race)

        # Ajout de nouvelles courses intermédiaires
        for race_params in simulation_params.get("intermediate_races", []):
            if not any(race.race_date == race_params.get("race_date") for race in user_data.intermediate_races):
                new_race = Course(
                    race_date=race_params["race_date"],
                    race_type=race_params["race_type"],
                    distance=race_params.get("distance"),
                    target_pace=race_params.get("target_pace"),
                    is_main_race=False
                )
                intermediate_races.append(new_race)

        # Construction du profil utilisateur modifié
        modified_user_data = UserData(
            start_date=simulation_params.get("start_date", user_data.start_date),
            main_race=main_race,
            pace_5k=simulation_params.get("pace_5k", user_data.pace_5k),
            pace_10k=simulation_params.get("pace_10k", user_data.pace_10k),
            pace_half_marathon=simulation_params.get("pace_half_marathon", user_data.pace_half_marathon),
            pace_marathon=simulation_params.get("pace_marathon", user_data.pace_marathon),
            sessions_per_week=simulation_params.get("sessions_per_week", user_data.sessions_per_week),
            min_volume=simulation_params.get("min_volume", user_data.min_volume),
            max_volume=simulation_params.get("max_volume", user_data.max_volume),
            intermediate_races=intermediate_races
        )

        return modified_user_data

    def _count_session_types(self, plan: TrainingPlan) -> Dict[str, int]:
        """
        Analyse la distribution des types de séances dans un plan.

        Args:
            plan: Plan d'entraînement à analyser

        Returns:
            Dictionnaire comptabilisant chaque type de séance
        """
        type_counts = {}

        for session in plan.sessions.values():
            session_type = session.session_type.value
            type_counts[session_type] = type_counts.get(session_type, 0) + 1

        return type_counts