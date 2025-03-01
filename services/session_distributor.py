"""
Service de distribution des séances d'entraînement.
"""
from datetime import date, timedelta
from typing import Dict, List, Tuple, Optional, Set
import random

from models.course import Course
from models.session import Session, SessionType, TrainingPhase, SessionBlock
from config.constants import (
    DEFAULT_LONG_RUN_DAY,
    DEFAULT_THRESHOLD_DAY,
    REST_DAY_PRIORITY,
    LONG_RUN_VOLUME_RATIO,
    THRESHOLD_VOLUME_RATIO,
    EF_VOLUME_RATIO,
    THRESHOLD_INTERVAL_MINUTES
)
from utils.date_utils import get_date_from_week_and_day, get_week_number


class SessionDistributor:
    """Distribue les séances d'entraînement selon les règles définies"""

    def __init__(self):
        # Générer une seed pour les opérations aléatoires (pour reproductibilité)
        self.random_seed = 42
        random.seed(self.random_seed)

        # Garder une trace des intervalles de seuil pour alterner
        self._threshold_interval_idx = 0

    def distribute_sessions(self, start_date: date, phases: Dict[TrainingPhase, List[date]],
                            weekly_volumes: Dict[int, float], sessions_per_week: int,
                            ef_pace: timedelta, specific_pace: timedelta,
                            intermediate_races: List[Course] = None) -> Dict[date, Session]:
        """
        Distribue les séances d'entraînement sur le calendrier

        Args:
            start_date: Date de début du plan
            phases: Dictionnaire des phases d'entraînement et leurs dates
            weekly_volumes: Dictionnaire des volumes hebdomadaires
            sessions_per_week: Nombre de séances par semaine
            ef_pace: Allure d'endurance fondamentale
            specific_pace: Allure spécifique de la course
            intermediate_races: Liste des courses intermédiaires

        Returns:
            Dictionnaire des séances indexées par date
        """
        if intermediate_races is None:
            intermediate_races = []

        # Initialiser le dictionnaire des séances
        sessions = {}

        # Trouver la date de course principale (dernière journée du plan)
        race_dates = [race.race_date for race in intermediate_races]

        # Trouver la dernière date du plan
        last_date = None
        for phase_dates in phases.values():
            if phase_dates:
                if last_date is None or max(phase_dates) > last_date:
                    last_date = max(phase_dates)

        # Si c'est la dernière semaine (semaine de la course), on doit s'assurer
        # qu'elle contient la course principale
        main_race_date = last_date

        # Traiter chaque semaine pour déterminer le placement des séances
        for week_idx, volume in weekly_volumes.items():
            # Déterminer la phase de la semaine
            week_start = start_date + timedelta(days=week_idx * 7)
            week_end = week_start + timedelta(days=6)
            week_dates = [week_start + timedelta(days=i) for i in range(7)]

            # Vérifier si cette semaine contient la course principale
            is_main_race_week = any(d == main_race_date for d in week_dates)

            # Déterminer la phase prédominante de la semaine
            week_phase_counts = {phase: 0 for phase in TrainingPhase}
            for day in week_dates:
                for phase, phase_dates in phases.items():
                    if day in phase_dates:
                        week_phase_counts[phase] += 1
                        break

            week_phase = max(week_phase_counts.items(), key=lambda x: x[1])[0]

            # Vérifier s'il y a une course intermédiaire cette semaine
            week_races = [race for race in intermediate_races
                          if any(day == race.race_date for day in week_dates)]

            has_intermediate_race = len(week_races) > 0
            intermediate_race = week_races[0] if has_intermediate_race else None

            # Distribuer les séances pour cette semaine, en tenant compte
            # de la spécificité de la semaine d'affûtage
            week_sessions = self._distribute_week_sessions(
                week_idx, week_start, week_phase, volume,
                sessions_per_week, ef_pace, specific_pace,
                intermediate_race,
                is_main_race_week=is_main_race_week,
                main_race_date=main_race_date if is_main_race_week else None
            )

            # Ajouter les séances au dictionnaire global
            sessions.update(week_sessions)

        return sessions

    def _distribute_week_sessions(self, week_idx: int, week_start: date, phase: TrainingPhase,
                                  volume: float, sessions_per_week: int,
                                  ef_pace: timedelta, specific_pace: timedelta,
                                  intermediate_race: Optional[Course] = None,
                                  is_main_race_week: bool = False,
                                  main_race_date: Optional[date] = None) -> Dict[date, Session]:
        """
        Distribue les séances pour une semaine spécifique

        Args:
            week_idx: Indice de la semaine
            week_start: Date de début de la semaine (lundi)
            phase: Phase d'entraînement de la semaine
            volume: Volume hebdomadaire (km)
            sessions_per_week: Nombre de séances par semaine
            ef_pace: Allure d'endurance fondamentale
            specific_pace: Allure spécifique de la course
            intermediate_race: Course intermédiaire de la semaine (si présente)
            is_main_race_week: Si True, cette semaine contient la course principale
            main_race_date: Date de la course principale (si dans cette semaine)

        Returns:
            Dictionnaire des séances de la semaine indexées par date
        """
        sessions = {}

        # L'allure "hors seuil" ou allure de récupération est l'allure EF (Endurance Fondamentale)
        # Cette allure est utilisée pour les phases d'échauffement, récupération et retour au calme

        # Déterminer les jours d'entraînement et de repos
        training_days, rest_days = self._get_training_and_rest_days(sessions_per_week)

        # S'il s'agit de la semaine de course principale, ajuster les jours d'entraînement
        if is_main_race_week and main_race_date:
            race_day = main_race_date.weekday()

            # Ajouter la course principale
            race_session = Session.create_race_session(
                session_date=main_race_date,
                phase=phase,
                race_distance=10.0,  # Pour 10K, à ajuster selon le type de course
                race_pace=specific_pace,
                description="Course principale: 10K",
                is_intermediate=False
            )

            sessions[main_race_date] = race_session

            # Retirer le jour de course des jours d'entraînement s'il y est
            if race_day in training_days:
                training_days.remove(race_day)
            # Et s'il était un jour de repos, récupérer un jour d'entraînement
            elif race_day in rest_days:
                rest_days.remove(race_day)
                # Ajouter un jour de repos parmi les jours d'entraînement
                if training_days:
                    new_rest_day = training_days.pop()
                    rest_days.add(new_rest_day)

        # Calculer les volumes par type de séance
        has_threshold = phase != TrainingPhase.TAPER and not intermediate_race

        if has_threshold:
            long_run_volume = volume * LONG_RUN_VOLUME_RATIO
            threshold_volume = volume * THRESHOLD_VOLUME_RATIO
            ef_volume = volume * EF_VOLUME_RATIO
        else:
            # Phase d'affûtage ou semaine avec course intermédiaire
            long_run_volume = volume * LONG_RUN_VOLUME_RATIO
            threshold_volume = 0
            ef_volume = volume - long_run_volume

        # Si c'est la semaine d'affûtage finale (avec la course principale),
        # ajuster les volumes pour garder des séances légères
        if is_main_race_week:
            # Réduire les volumes pour la semaine de course principale
            # Les séances légères sont maintenues pour garder le tonus musculaire
            long_run_volume = min(long_run_volume, 5.0)  # Limiter à 5 km max
            ef_volume = volume - long_run_volume

        # Placer les séances clés

        # 1. Course intermédiaire (si présente)
        if intermediate_race:
            race_date = intermediate_race.race_date
            race_day = race_date.weekday()

            # Créer la séance de course
            race_session = Session.create_race_session(
                session_date=race_date,
                phase=phase,
                race_distance=intermediate_race.get_standard_distance,
                race_pace=intermediate_race.target_pace or specific_pace,
                description=f"Course intermédiaire: {intermediate_race.race_type.value}",
                is_intermediate=True
            )

            sessions[race_date] = race_session

            # Ajuster les jours d'entraînement
            if race_day in training_days:
                training_days.remove(race_day)
            elif rest_days:
                # Si le jour de course est un jour de repos, ajuster un autre jour
                rest_day = rest_days.pop()  # Prendre un jour de repos
                training_days.append(rest_day)  # Le transformer en jour d'entraînement

        # 2. Sortie longue (SL), sauf si elle tombe le jour de la course principale
        # Dans ce cas elle a déjà été remplacée par la course principale
        if not (is_main_race_week and main_race_date and main_race_date.weekday() == DEFAULT_LONG_RUN_DAY):
            long_run_day = DEFAULT_LONG_RUN_DAY

            # Vérifier si le jour par défaut est disponible
            if long_run_day not in training_days and intermediate_race and intermediate_race.race_date.weekday() == long_run_day:
                # La SL est remplacée par la course intermédiaire
                pass
            elif long_run_day not in training_days:
                # Choisir un autre jour pour la SL
                available_days = list(training_days)
                if available_days:
                    long_run_day = available_days[0]  # Prendre le premier jour disponible
                else:
                    long_run_day = None  # Pas de jour disponible pour la SL

            if long_run_day is not None and long_run_day in training_days:
                long_run_date = week_start + timedelta(days=long_run_day)

                if long_run_date not in sessions:  # Vérifier qu'il n'y a pas déjà une course ce jour
                    # Créer la séance de sortie longue
                    long_run_session = Session.create_long_run_session(
                        session_date=long_run_date,
                        phase=phase,
                        total_distance=long_run_volume,
                        ef_pace=ef_pace,
                        specific_pace=specific_pace if phase == TrainingPhase.SPECIFIC else None
                    )

                    sessions[long_run_date] = long_run_session
                    training_days.remove(long_run_day)

        # 3. Séance de seuil (si nécessaire)
        if has_threshold:
            threshold_day = DEFAULT_THRESHOLD_DAY

            # Vérifier si le jour par défaut est disponible
            if threshold_day not in training_days:
                # Choisir un autre jour pour le seuil
                available_days = list(training_days)
                if available_days:
                    threshold_day = available_days[0]  # Prendre le premier jour disponible
                else:
                    threshold_day = None  # Pas de jour disponible pour le seuil

            if threshold_day is not None:
                threshold_date = week_start + timedelta(days=threshold_day)

                # Déterminer l'intervalle pour cette séance de seuil
                if phase == TrainingPhase.SPECIFIC:
                    # En phase spécifique, utiliser l'allure de la course principale
                    interval_minutes = THRESHOLD_INTERVAL_MINUTES.get("other", [2, 3])
                    if isinstance(interval_minutes, list):
                        interval_minute = interval_minutes[self._threshold_interval_idx % len(interval_minutes)]
                        self._threshold_interval_idx += 1
                    else:
                        interval_minute = interval_minutes
                else:
                    # En phase développement, alterner les allures
                    interval_minutes = THRESHOLD_INTERVAL_MINUTES.get("other", [2, 3])
                    if isinstance(interval_minutes, list):
                        interval_minute = interval_minutes[self._threshold_interval_idx % len(interval_minutes)]
                        self._threshold_interval_idx += 1
                    else:
                        interval_minute = interval_minutes

                # Créer la séance de seuil
                threshold_session = Session.create_threshold_session(
                    session_date=threshold_date,
                    phase=phase,
                    total_distance=threshold_volume,
                    ef_pace=ef_pace,
                    threshold_pace=specific_pace,
                    interval_minutes=interval_minute
                )

                sessions[threshold_date] = threshold_session
                training_days.remove(threshold_day)

        # 4. Séances d'endurance fondamentale (EF)
        # Répartir le volume EF entre les jours restants
        ef_days_count = len(training_days)

        if ef_days_count > 0:
            # Particulièrement important pour la phase d'affûtage
            ef_volumes = self._distribute_ef_volumes(ef_volume, ef_days_count)

            for i, day in enumerate(sorted(training_days)):
                ef_date = week_start + timedelta(days=day)

                # Pour la semaine de la course, placer les séances EF
                # principalement en début de semaine
                desc = "Séance d'endurance fondamentale légère" if is_main_race_week else f"Séance d'endurance fondamentale de {ef_volumes[i]} km"

                # Créer la séance EF
                ef_session = Session.create_ef_session(
                    session_date=ef_date,
                    phase=phase,
                    distance=ef_volumes[i],
                    ef_pace=ef_pace,
                    description=desc
                )

                sessions[ef_date] = ef_session

        # 5. Jours de repos
        for day in rest_days:
            rest_date = week_start + timedelta(days=day)

            # Ne pas créer de séance de repos si une course est déjà prévue ce jour
            if rest_date not in sessions:
                # Créer la séance de repos
                rest_session = Session.create_rest_session(
                    session_date=rest_date,
                    phase=phase
                )

                sessions[rest_date] = rest_session

        return sessions

    def _get_training_and_rest_days(self, sessions_per_week: int) -> Tuple[Set[int], Set[int]]:
        """
        Détermine les jours d'entraînement et de repos

        Args:
            sessions_per_week: Nombre de séances par semaine

        Returns:
            Tuple (jours d'entraînement, jours de repos)
        """
        all_days = set(range(7))  # 0 = lundi, 6 = dimanche
        rest_days_count = 7 - sessions_per_week

        # Sélectionner les jours de repos selon l'ordre de priorité
        rest_days = set()
        for day in REST_DAY_PRIORITY:
            if len(rest_days) < rest_days_count:
                rest_days.add(day)
            else:
                break

        # Jours d'entraînement = tous les jours sauf jours de repos
        training_days = all_days - rest_days

        return training_days, rest_days

    def _distribute_ef_volumes(self, total_volume: float, sessions_count: int) -> List[float]:
        """
        Distribue le volume total d'EF entre plusieurs séances

        Args:
            total_volume: Volume total à distribuer (km)
            sessions_count: Nombre de séances

        Returns:
            Liste des volumes pour chaque séance (km)
        """
        if sessions_count <= 0:
            return []

        if sessions_count == 1:
            return [round(total_volume, 1)]

        # Distribuer les volumes en utilisant des coefficients différents
        # pour éviter d'avoir des séances identiques
        min_coef = 0.15
        max_coef = 0.6

        # Générer des coefficients aléatoires
        coefficients = []
        for _ in range(sessions_count):
            coef = random.uniform(min_coef, max_coef)
            coefficients.append(coef)

        # Normaliser les coefficients pour qu'ils somment à 1
        total_coef = sum(coefficients)
        normalized_coefficients = [c / total_coef for c in coefficients]

        # Calculer les volumes (arrondis au dixième)
        volumes = [round(total_volume * coef, 1) for coef in normalized_coefficients]

        # Ajuster pour que la somme soit égale au volume total
        current_sum = sum(volumes)
        if abs(current_sum - total_volume) > 0.1:
            # Ajouter/soustraire la différence au plus grand volume
            diff = total_volume - current_sum
            max_idx = volumes.index(max(volumes))
            volumes[max_idx] = round(volumes[max_idx] + diff, 1)

        return volumes