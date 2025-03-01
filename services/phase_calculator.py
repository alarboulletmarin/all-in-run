"""
Service de calcul des phases d'entraînement.
"""
from datetime import date, timedelta
from typing import Dict, List, Tuple

from config.constants import (
    MIN_TAPER_WEEKS,
    TAPER_PHASE_RATIO,
    DEVELOPMENT_SPECIFIC_RATIO
)
from models.session import TrainingPhase
from utils.date_utils import get_days_between, get_weeks_between, get_date_from_week_and_day


class PhaseCalculator:
    """Calcule les phases d'entraînement selon les règles définies"""

    def calculate_phases(self, start_date: date, race_date: date) -> Dict[TrainingPhase, List[date]]:
        """
        Calcule les phases d'entraînement et leurs dates

        Args:
            start_date: Date de début du plan (lundi)
            race_date: Date de la course (dimanche)

        Returns:
            Dictionnaire avec les phases comme clés et les listes de dates comme valeurs
        """
        # Calculer le nombre total de semaines
        total_weeks = get_weeks_between(start_date, race_date)
        num_weeks = len(total_weeks)

        # Nombre de semaines pour chaque phase
        taper_weeks = max(MIN_TAPER_WEEKS, round(num_weeks * TAPER_PHASE_RATIO))
        remaining_weeks = num_weeks - taper_weeks

        # Répartir selon le ratio 4:3 entre développement et spécifique
        dev_ratio = DEVELOPMENT_SPECIFIC_RATIO / (1 + DEVELOPMENT_SPECIFIC_RATIO)
        development_weeks = round(remaining_weeks * dev_ratio)
        specific_weeks = remaining_weeks - development_weeks

        # Calcul des dates pour chaque phase
        phases = {}

        # Phase de développement
        development_dates = []
        for week_idx in range(development_weeks):
            week_start = start_date + timedelta(days=week_idx * 7)
            for day_offset in range(7):
                current_date = week_start + timedelta(days=day_offset)
                development_dates.append(current_date)

        phases[TrainingPhase.DEVELOPMENT] = development_dates

        # Phase spécifique
        specific_start = start_date + timedelta(days=development_weeks * 7)
        specific_dates = []
        for week_idx in range(specific_weeks):
            week_start = specific_start + timedelta(days=week_idx * 7)
            for day_offset in range(7):
                current_date = week_start + timedelta(days=day_offset)
                specific_dates.append(current_date)

        phases[TrainingPhase.SPECIFIC] = specific_dates

        # Phase d'affûtage
        taper_start = specific_start + timedelta(days=specific_weeks * 7)
        taper_dates = []
        for week_idx in range(taper_weeks):
            week_start = taper_start + timedelta(days=week_idx * 7)
            for day_offset in range(7):
                current_date = week_start + timedelta(days=day_offset)
                if current_date <= race_date:
                    taper_dates.append(current_date)

        phases[TrainingPhase.TAPER] = taper_dates

        return phases

    def get_phase_for_date(self, phases: Dict[TrainingPhase, List[date]],
                           target_date: date) -> TrainingPhase:
        """
        Détermine la phase d'entraînement pour une date donnée

        Args:
            phases: Dictionnaire des phases et leurs dates
            target_date: Date pour laquelle déterminer la phase

        Returns:
            Phase d'entraînement correspondante
        """
        for phase, dates in phases.items():
            if target_date in dates:
                return phase

        # Si la date n'est dans aucune phase connue, retourner la dernière phase
        # (utile pour les dates postérieures à la course)
        if target_date > max(phases[TrainingPhase.TAPER]):
            return TrainingPhase.TAPER

        # Sinon, retourner la première phase
        return TrainingPhase.DEVELOPMENT

    def get_phase_weeks(self, phases: Dict[TrainingPhase, List[date]]) -> Dict[TrainingPhase, int]:
        """
        Compte le nombre de semaines dans chaque phase

        Args:
            phases: Dictionnaire des phases et leurs dates

        Returns:
            Dictionnaire avec les phases comme clés et le nombre de semaines comme valeurs
        """
        phase_weeks = {}

        for phase, dates in phases.items():
            if not dates:
                phase_weeks[phase] = 0
                continue

            min_date = min(dates)
            max_date = max(dates)

            # Ajuster pour obtenir des semaines complètes
            min_date = min_date - timedelta(days=min_date.weekday())  # Ramener au lundi
            if max_date.weekday() < 6:  # Si pas un dimanche
                max_date = max_date + timedelta(days=6 - max_date.weekday())  # Étendre au dimanche

            weeks = get_weeks_between(min_date, max_date)
            phase_weeks[phase] = len(weeks)

        return phase_weeks

    def get_phase_boundaries(self, phases: Dict[TrainingPhase, List[date]]) -> Dict[TrainingPhase, Tuple[date, date]]:
        """
        Obtient les dates de début et de fin de chaque phase

        Args:
            phases: Dictionnaire des phases et leurs dates

        Returns:
            Dictionnaire avec les phases comme clés et les tuples (début, fin) comme valeurs
        """
        boundaries = {}

        for phase, dates in phases.items():
            if not dates:
                continue

            boundaries[phase] = (min(dates), max(dates))

        return boundaries

    def get_week_phase(self, phases: Dict[TrainingPhase, List[date]],
                       week_start: date) -> TrainingPhase:
        """
        Détermine la phase d'entraînement pour une semaine donnée

        Args:
            phases: Dictionnaire des phases et leurs dates
            week_start: Date de début de la semaine (lundi)

        Returns:
            Phase d'entraînement prédominante pour la semaine
        """
        # Générer les dates de la semaine
        week_dates = [week_start + timedelta(days=i) for i in range(7)]

        # Compter le nombre de jours dans chaque phase
        phase_counts = {phase: 0 for phase in TrainingPhase}

        for day in week_dates:
            for phase, dates in phases.items():
                if day in dates:
                    phase_counts[phase] += 1
                    break

        # Retourner la phase avec le plus de jours dans la semaine
        return max(phase_counts.items(), key=lambda x: x[1])[0]