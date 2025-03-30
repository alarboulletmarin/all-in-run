from datetime import timedelta
from typing import Dict, Optional

from models.course import RaceType


def calculate_ef_pace(marathon_pace: timedelta) -> timedelta:
    """
    Calcule l'allure d'endurance fondamentale (marathon + 30s)

    Args:
        marathon_pace: Allure marathon en min/km

    Returns:
        Allure d'endurance fondamentale
    """
    marathon_seconds = marathon_pace.total_seconds()
    ef_seconds = marathon_seconds + 30
    return timedelta(seconds=ef_seconds)


def calculate_specific_ef_pace(race_pace: timedelta, pace_10k: timedelta,
                               pace_marathon: timedelta) -> timedelta:
    """
    Calcule l'allure d'endurance fondamentale pour les courses de type 'autre'
    selon les règles spécifiques

    Args:
        race_pace: Allure calculée pour la course
        pace_10k: Allure 10K de référence
        pace_marathon: Allure marathon de référence

    Returns:
        Allure d'endurance fondamentale spécifique
    """
    # Convertir en secondes pour faciliter les comparaisons
    race_seconds = race_pace.total_seconds()
    pace_10k_seconds = pace_10k.total_seconds()
    pace_marathon_seconds = pace_marathon.total_seconds()

    # Appliquer les règles spécifiques
    if race_seconds < pace_10k_seconds:
        # Plus rapide que l'allure 10K: +40s
        ef_seconds = race_seconds + 40
    elif race_seconds < pace_marathon_seconds:
        # Entre l'allure 10K et marathon: +30s
        ef_seconds = race_seconds + 30
    else:
        # Plus lente que l'allure marathon: +20s
        ef_seconds = race_seconds + 20

    return timedelta(seconds=ef_seconds)


def calculate_race_pace(race_type: RaceType, distance: Optional[float],
                        target_time: Optional[timedelta],
                        pace_5k: timedelta, pace_10k: timedelta,
                        pace_half_marathon: timedelta,
                        pace_marathon: timedelta) -> timedelta:
    """
    Calcule l'allure spécifique pour un type de course donné

    Args:
        race_type: Type de course
        distance: Distance en km (utilisée uniquement si race_type est OTHER)
        target_time: Temps cible (utilisé uniquement si race_type est OTHER)
        pace_5k: Allure 5K de référence
        pace_10k: Allure 10K de référence
        pace_half_marathon: Allure semi-marathon de référence
        pace_marathon: Allure marathon de référence

    Returns:
        Allure spécifique pour la course
    """
    if race_type == RaceType.TEN_K:
        return pace_10k
    elif race_type == RaceType.HALF_MARATHON:
        return pace_half_marathon
    elif race_type == RaceType.MARATHON:
        return pace_marathon
    elif race_type == RaceType.OTHER:
        # Pour les courses de type "autre", calculer à partir de la distance et du temps cible
        if distance is None or target_time is None:
            raise ValueError("Distance et temps cible requis pour les courses de type 'autre'")

        # Allure = temps total / distance
        seconds_per_km = target_time.total_seconds() / distance
        return timedelta(seconds=seconds_per_km)
    else:
        raise ValueError(f"Type de course non pris en charge: {race_type}")


def estimate_race_time(target_distance: float, reference_distance: float,
                       reference_time: timedelta) -> timedelta:
    """
    Estime le temps de course pour une distance cible à partir d'une référence
    Utilise la formule de Riegel: T2 = T1 * (D2/D1)^1.06

    Args:
        target_distance: Distance cible en km
        reference_distance: Distance de référence en km
        reference_time: Temps de référence en timedelta

    Returns:
        Temps estimé pour la distance cible
    """
    if reference_distance <= 0 or target_distance <= 0:
        raise ValueError("Les distances doivent être positives")

    # Formule de Riegel: T2 = T1 * (D2/D1)^1.06
    ratio = (target_distance / reference_distance) ** 1.06
    target_seconds = reference_time.total_seconds() * ratio

    return timedelta(seconds=round(target_seconds))


def estimate_race_pace(target_distance: float, reference_distance: float,
                       reference_pace: timedelta) -> timedelta:
    """
    Estime l'allure de course pour une distance cible à partir d'une référence

    Args:
        target_distance: Distance cible en km
        reference_distance: Distance de référence en km
        reference_pace: Allure de référence en min/km

    Returns:
        Allure estimée pour la distance cible
    """
    if reference_distance <= 0 or target_distance <= 0:
        raise ValueError("Les distances doivent être positives")

    # Convertir l'allure en temps total pour la distance de référence
    reference_time = timedelta(seconds=reference_pace.total_seconds() * reference_distance)

    # Estimer le temps pour la distance cible
    target_time = estimate_race_time(target_distance, reference_distance, reference_time)

    # Reconvertir en allure
    target_pace = timedelta(seconds=target_time.total_seconds() / target_distance)

    return target_pace


def get_equivalent_paces(reference_pace: timedelta, reference_distance: float) -> Dict[str, timedelta]:
    """
    Calcule les allures équivalentes pour différentes distances
    à partir d'une allure de référence

    Args:
        reference_pace: Allure de référence en min/km
        reference_distance: Distance de référence en km

    Returns:
        Dictionnaire des allures équivalentes pour 5K, 10K, semi et marathon
    """
    distances = {
        "5K": 5.0,
        "10K": 10.0,
        "half_marathon": 21.1,
        "marathon": 42.2
    }

    equivalent_paces = {}

    for name, distance in distances.items():
        equivalent_paces[name] = estimate_race_pace(distance, reference_distance, reference_pace)

    return equivalent_paces


def get_vdot_from_pace(pace: timedelta, distance: float) -> float:
    """
    Estime la valeur VO2max (VDOT) à partir d'une allure et d'une distance
    selon le modèle de Jack Daniels (approximation simplifiée)

    Args:
        pace: Allure en min/km
        distance: Distance en km

    Returns:
        Valeur VDOT estimée
    """
    # Conversion de l'allure en m/s pour les calculs
    pace_seconds_per_km = pace.total_seconds()
    speed_m_s = 1000 / pace_seconds_per_km

    # Durée de l'effort en secondes
    duration_seconds = distance * pace_seconds_per_km

    # Facteurs d'ajustement selon la durée (approximation)
    if duration_seconds < 420:  # Moins de 7 minutes
        adjustment = 0.97
    elif duration_seconds < 900:  # Moins de 15 minutes
        adjustment = 0.98
    elif duration_seconds < 1800:  # Moins de 30 minutes
        adjustment = 0.99
    elif duration_seconds < 3600:  # Moins de 60 minutes
        adjustment = 1.0
    elif duration_seconds < 7200:  # Moins de 2 heures
        adjustment = 1.01
    else:  # 2 heures ou plus
        adjustment = 1.02

    # Formule simplifiée basée sur le modèle de Jack Daniels
    # VDOT = (speed_m_s * 0.2989558 + 0.1694) * adjustment
    vdot = (speed_m_s * 0.2989558 + 0.1694) * adjustment * 100

    return round(vdot, 1)


def get_training_paces_from_vdot(vdot: float) -> Dict[str, timedelta]:
    """
    Calcule les allures d'entraînement recommandées à partir d'une valeur VDOT
    selon le modèle de Jack Daniels (approximation simplifiée)

    Args:
        vdot: Valeur VDOT

    Returns:
        Dictionnaire des allures d'entraînement recommandées
    """
    # Facteur de conversion VDOT -> vitesse (approximation)
    vdot_factor = vdot / 100

    # Coefficients pour différentes zones d'entraînement (approximation)
    pace_coefs = {
        "easy": 0.76,  # Allure facile (endurance fondamentale)
        "marathon": 0.83,  # Allure marathon
        "threshold": 0.88,  # Allure seuil
        "interval": 0.95,  # Allure intervalle (10K-5K)
        "repetition": 1.05  # Allure répétition (plus rapide que 5K)
    }

    training_paces = {}

    for name, coef in pace_coefs.items():
        # Vitesse en m/s
        speed_m_s = (vdot_factor - 0.1694) / 0.2989558 * coef

        # Conversion en pace (s/km puis timedelta)
        if speed_m_s > 0:
            seconds_per_km = 1000 / speed_m_s
            training_paces[name] = timedelta(seconds=seconds_per_km)
        else:
            # Éviter la division par zéro
            training_paces[name] = timedelta(minutes=30)  # Valeur arbitraire élevée

    return training_paces