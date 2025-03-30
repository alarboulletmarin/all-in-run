from datetime import date, timedelta
from typing import Dict, List

from models.course import Course
from models.session import TrainingPhase
from config.constants import (
    VOLUME_REDUCTION_RACE_WEEK,
    CHARGE_DISCHARGE_PATTERN,
    DISCHARGE_REDUCTION,
    TAPER_FINAL_WEEK_RATIO
)

class VolumeCalculator:
    """Calcule les volumes hebdomadaires selon les règles définies"""

    def calculate_volumes(self, min_volume: float, max_volume: float,
                          phases: Dict[TrainingPhase, List[date]],
                          intermediate_races: List[Course] = None) -> Dict[int, float]:
        """
        Calcule les volumes hebdomadaires pour chaque semaine du plan

        Args:
            min_volume: Volume hebdomadaire minimal (km)
            max_volume: Volume hebdomadaire maximal (km)
            phases: Dictionnaire des phases d'entraînement et leurs dates
            intermediate_races: Liste des courses intermédiaires

        Returns:
            Dictionnaire avec les indices de semaine (0-indexed) comme clés
            et les volumes hebdomadaires (km) comme valeurs
        """
        # Initialiser les courses intermédiaires
        if intermediate_races is None:
            intermediate_races = []

        # Obtenir les dates de début et de fin de chaque phase
        phase_boundaries = {}
        for phase, dates in phases.items():
            if dates:
                phase_boundaries[phase] = (min(dates), max(dates))

        # Déterminer le nombre total de semaines
        if not phase_boundaries:
            return {}

        start_date = min([boundaries[0] for boundaries in phase_boundaries.values()])
        end_date = max([boundaries[1] for boundaries in phase_boundaries.values()])

        # Générer les semaines (lundi au dimanche)
        weeks = []
        current_date = start_date
        while current_date <= end_date:
            # S'assurer que la date est un lundi
            if current_date.weekday() != 0:
                current_date = current_date - timedelta(days=current_date.weekday())

            # Fin de la semaine (dimanche)
            week_end = current_date + timedelta(days=6)
            weeks.append((current_date, week_end))

            # Passer à la semaine suivante
            current_date = current_date + timedelta(days=7)

        # Déterminer les semaines pour chaque phase
        dev_weeks = []
        specific_weeks = []
        taper_weeks = []

        for i, (week_start, week_end) in enumerate(weeks):
            # Compter le nombre de jours dans chaque phase
            days_in_phase = {phase: 0 for phase in TrainingPhase}

            for day_offset in range(7):
                day_date = week_start + timedelta(days=day_offset)
                for phase, dates in phases.items():
                    if day_date in dates:
                        days_in_phase[phase] += 1
                        break

            # Assigner la semaine à la phase qui a le plus de jours
            predominant_phase = max(days_in_phase.items(), key=lambda x: x[1])[0]

            if predominant_phase == TrainingPhase.DEVELOPMENT:
                dev_weeks.append(i)
            elif predominant_phase == TrainingPhase.SPECIFIC:
                specific_weeks.append(i)
            elif predominant_phase == TrainingPhase.TAPER:
                taper_weeks.append(i)

        # Calculer les volumes hebdomadaires
        volumes = {}

        # IMPORTANT: S'assurer que toutes les semaines ont un volume
        all_weeks = set(i for i in range(len(weeks)))

        # 1. Calculer pour les phases développement et spécifique
        # Calculer le volume initial et final pour les phases de développement et spécifique
        initial_volume = min_volume
        final_volume = max_volume

        # Nombre de semaines à charge (hors décharge)
        dev_specific_weeks = sorted(dev_weeks + specific_weeks)
        charge_pattern = {}
        pattern_index = 0

        for i in dev_specific_weeks:
            charge_pattern[i] = CHARGE_DISCHARGE_PATTERN[pattern_index % len(CHARGE_DISCHARGE_PATTERN)]
            pattern_index += 1

        charge_weeks_count = sum(1 for i in dev_specific_weeks if charge_pattern.get(i, 0) == 1)

        if charge_weeks_count > 1:
            # Progression linéaire des semaines à charge
            volume_increment = (final_volume - initial_volume) / (charge_weeks_count - 1)
        else:
            volume_increment = 0

        # Calculer le volume pour chaque semaine de développement et spécifique
        current_volume = initial_volume
        last_charge_volume = initial_volume

        for i in dev_specific_weeks:
            if charge_pattern.get(i, 0) == 1:  # Semaine à charge
                volumes[i] = current_volume
                last_charge_volume = current_volume
                current_volume += volume_increment
            else:  # Semaine à décharge
                volumes[i] = last_charge_volume * (1 - DISCHARGE_REDUCTION)

        # 2. Calculer pour les semaines d'affûtage
        taper_weeks = sorted(taper_weeks)

        if taper_weeks:
            # Déterminer le volume de départ pour l'affûtage
            taper_start_volume = max(volumes.values()) if volumes else max_volume

            # Volume final = 50% du volume minimal pour l'avant-dernière semaine
            # et 20% pour la dernière semaine (qui contient la course)
            taper_final_volume = min_volume * TAPER_FINAL_WEEK_RATIO

            # Progression linéaire pour l'affûtage
            if len(taper_weeks) > 1:
                taper_decrement = (taper_start_volume - taper_final_volume) / (len(taper_weeks) - 1)
            else:
                taper_decrement = 0

            # Appliquer la réduction progressive
            current_taper_volume = taper_start_volume
            for i in taper_weeks:
                volumes[i] = current_taper_volume
                current_taper_volume -= taper_decrement

        # ASSUREZ-VOUS QUE TOUTES LES SEMAINES ONT UN VOLUME
        # C'est crucial pour que toutes les semaines soient traitées
        for week_idx in all_weeks:
            if week_idx not in volumes:
                # Semaine sans volume assigné (rare, mais possible)
                # Assigner un volume par défaut basé sur la phase
                if week_idx in taper_weeks:
                    volumes[week_idx] = min_volume * 0.5  # 50% du volume minimal
                else:
                    volumes[week_idx] = min_volume

        # 3. Appliquer la réduction pour les semaines avec courses intermédiaires
        for race in intermediate_races:
            race_date = race.race_date

            # Trouver la semaine de la course
            for i, (week_start, week_end) in enumerate(weeks):
                if week_start <= race_date <= week_end:
                    # Réduire le volume de la semaine de course
                    if i in volumes:
                        volumes[i] = volumes[i] * (1 - VOLUME_REDUCTION_RACE_WEEK)
                    break

        # Arrondir les volumes au dixième
        volumes = {week: round(volume, 1) for week, volume in volumes.items()}

        # Vérification finale: s'assurer qu'aucun volume n'est à zéro
        for week_idx in volumes:
            if volumes[week_idx] <= 0:
                volumes[week_idx] = max(min_volume * 0.2, 5.0)  # Au moins 5 km ou 20% du min

        return volumes

    def distribute_sessions_volume(self, total_volume: float, sessions_count: int) -> List[float]:
        """
        Distribue le volume total entre plusieurs séances d'endurance fondamentale

        Args:
            total_volume: Volume total à distribuer (km)
            sessions_count: Nombre de séances

        Returns:
            Liste des volumes pour chaque séance (km)
        """
        if sessions_count <= 0:
            return []

        if sessions_count == 1:
            return [total_volume]

        # Distribuer les volumes en utilisant des coefficients différents
        # pour éviter d'avoir des séances identiques

        # Générer des coefficients aléatoires entre 0.15 et 0.6
        import random
        random.seed(total_volume + sessions_count)  # Pour la reproductibilité

        coefficients = []
        min_coef = 0.15
        max_coef = 0.6

        for _ in range(sessions_count):
            coef = random.uniform(min_coef, max_coef)
            coefficients.append(coef)

        # Normaliser les coefficients pour qu'ils somment à 1
        total_coef = sum(coefficients)
        normalized_coefficients = [c / total_coef for c in coefficients]

        # Calculer les volumes
        volumes = [round(total_volume * coef, 1) for coef in normalized_coefficients]

        # Ajuster pour éviter les volumes trop faibles
        min_volume = 2.0  # Volume minimal acceptable pour une séance
        for i, vol in enumerate(volumes):
            if vol < min_volume:
                volumes[i] = min_volume

        # Ajuster pour que la somme soit égale au volume total
        current_sum = sum(volumes)
        if current_sum != total_volume:
            # Répartir la différence proportionnellement
            diff = total_volume - current_sum
            for i in range(sessions_count):
                if i == sessions_count - 1:
                    # Dernier élément: prendre toute la différence restante
                    volumes[i] = round(volumes[i] + diff, 1)
                else:
                    # Répartir proportionnellement
                    adjustment = round(diff * normalized_coefficients[i], 1)
                    volumes[i] = round(volumes[i] + adjustment, 1)
                    diff -= adjustment

        return volumes

    def get_week_load_type(self, week_index: int,
                           volumes: Dict[int, float]) -> str:
        """
        Détermine le type de charge pour une semaine donnée

        Args:
            week_index: Indice de la semaine
            volumes: Dictionnaire des volumes hebdomadaires

        Returns:
            Type de charge ("charge", "decharge", "stable")
        """
        if week_index not in volumes:
            return "stable"

        # Vérifier s'il y a une semaine précédente
        if week_index - 1 in volumes:
            prev_volume = volumes[week_index - 1]
            current_volume = volumes[week_index]

            if current_volume > prev_volume * 1.05:  # 5% d'augmentation
                return "charge"
            elif current_volume < prev_volume * 0.95:  # 5% de diminution
                return "decharge"
            else:
                return "stable"

        return "stable"