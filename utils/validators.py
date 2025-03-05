"""
Validateurs pour les données utilisateur.
"""
from datetime import date, timedelta
from typing import Tuple, Dict, Any, List, Optional, Union
import re

from config.constants import MIN_WEEKS_BEFORE_RACE, MIN_SESSIONS_PER_WEEK, MAX_SESSIONS_PER_WEEK
from config.languages import VALIDATION_ERROR_TRANSLATIONS
from models.course import RaceType
from .time_converter import parse_time_string, parse_pace_string
from .translations import translate


def validate_date_range(start_date: date, race_date: date,
                        min_weeks: int = MIN_WEEKS_BEFORE_RACE,
                        lang: str = "fr") -> Tuple[bool, str]:
    """
    Valide que la plage de dates respecte les contraintes

    Args:
        start_date: Date de début (doit être un lundi)
        race_date: Date de course (doit être un dimanche)
        min_weeks: Nombre minimal de semaines entre start_date et race_date
        lang: Code de langue pour les messages d'erreur

    Returns:
        Tuple (valid, message)
    """
    # Vérifier que start_date est un lundi
    if start_date.weekday() != 0:
        return False, VALIDATION_ERROR_TRANSLATIONS.get(lang, {}).get(
            "start_date_monday", "La date de début doit être un lundi."
        )

    # Vérifier que race_date est un dimanche
    if race_date.weekday() != 6:
        return False, VALIDATION_ERROR_TRANSLATIONS.get(lang, {}).get(
            "race_date_sunday", "La date de course doit être un dimanche."
        )

    # Vérifier le nombre minimal de semaines
    days_diff = (race_date - start_date).days
    weeks_diff = days_diff // 7

    if weeks_diff < min_weeks:
        return False, VALIDATION_ERROR_TRANSLATIONS.get(lang, {}).get(
            "min_weeks", f"La préparation doit durer au moins {min_weeks} semaines."
        )

    return True, ""


def validate_course_info(race_type: Union[str, RaceType], distance: Optional[float],
                         target_time: Optional[str], lang: str = "fr") -> Tuple[bool, str]:
    """
    Valide les informations de course

    Args:
        race_type: Type de course
        distance: Distance (requise uniquement pour type "autre")
        target_time: Temps cible (requis uniquement pour type "autre")
        lang: Code de langue pour les messages d'erreur

    Returns:
        Tuple (valid, message)
    """
    # Convertir la chaîne en enum si nécessaire
    if isinstance(race_type, str):
        try:
            race_type = RaceType(race_type)
        except ValueError:
            return False, f"Type de course non reconnu: {race_type}"

    # Vérifier si la distance et le temps sont fournis pour le type "autre"
    if race_type == RaceType.OTHER:
        if distance is None or distance <= 0:
            return False, "La distance est obligatoire pour les courses de type 'autre'"

        if target_time is None or not target_time:
            return False, "Le temps cible est obligatoire pour les courses de type 'autre'"

        # Valider le format du temps cible
        time_delta = parse_time_string(target_time)
        if time_delta is None:
            return False, "Format de temps cible invalide. Utilisez le format hh:mm:ss"

    return True, ""


def validate_paces(pace_5k: str, pace_10k: str, pace_half: str, pace_marathon: str,
                   lang: str = "fr") -> Tuple[bool, str, Dict[str, timedelta]]:
    """
    Valide les allures saisies par l'utilisateur

    Args:
        pace_5k: Allure 5K au format mm:ss
        pace_10k: Allure 10K au format mm:ss
        pace_half: Allure semi-marathon au format mm:ss
        pace_marathon: Allure marathon au format mm:ss
        lang: Code de langue pour les messages d'erreur

    Returns:
        Tuple (valid, message, paces_dict)
    """
    # Valider le format des allures
    pace_5k_delta = parse_pace_string(pace_5k)
    pace_10k_delta = parse_pace_string(pace_10k)
    pace_half_delta = parse_pace_string(pace_half)
    pace_marathon_delta = parse_pace_string(pace_marathon)

    # Vérifier que toutes les allures ont été correctement converties
    if None in (pace_5k_delta, pace_10k_delta, pace_half_delta, pace_marathon_delta):
        return False, "Format d'allure invalide. Utilisez le format mm:ss", {}

    # Vérifier l'ordre des allures
    if not (pace_5k_delta < pace_10k_delta < pace_half_delta < pace_marathon_delta):
        return False, VALIDATION_ERROR_TRANSLATIONS.get(lang, {}).get(
            "pace_order", "Les allures doivent respecter l'ordre: 5K < 10K < Semi < Marathon."
        ), {}

    # Tout est valide, retourner le dictionnaire des allures
    paces_dict = {
        "pace_5k": pace_5k_delta,
        "pace_10k": pace_10k_delta,
        "pace_half_marathon": pace_half_delta,
        "pace_marathon": pace_marathon_delta
    }

    return True, "", paces_dict


def validate_volume(min_volume: float, max_volume: float, lang: str = "fr") -> Tuple[bool, str]:
    """
    Valide les volumes minimaux et maximaux

    Args:
        min_volume: Volume hebdomadaire minimal
        max_volume: Volume hebdomadaire maximal
        lang: Code de langue pour les messages d'erreur

    Returns:
        Tuple (valid, message)
    """
    # Vérifier que les volumes sont positifs
    if min_volume <= 0 or max_volume <= 0:
        return False, "Les volumes doivent être positifs"

    # Vérifier que max_volume > min_volume
    if min_volume >= max_volume:
        return False, VALIDATION_ERROR_TRANSLATIONS.get(lang, {}).get(
            "volume_order", "Le volume maximal doit être supérieur au volume minimal."
        )

    return True, ""


def validate_sessions_per_week(sessions: int, lang: str = "fr") -> Tuple[bool, str]:
    """
    Valide le nombre de séances par semaine

    Args:
        sessions: Nombre de séances par semaine
        lang: Code de langue pour les messages d'erreur

    Returns:
        Tuple (valid, message)
    """
    if not (MIN_SESSIONS_PER_WEEK <= sessions <= MAX_SESSIONS_PER_WEEK):
        return False, VALIDATION_ERROR_TRANSLATIONS.get(lang, {}).get(
            "sessions_range", f"Le nombre de séances par semaine doit être entre {MIN_SESSIONS_PER_WEEK} et {MAX_SESSIONS_PER_WEEK}."
        )

    return True, ""


def validate_intermediate_races(intermediate_races: List[Dict[str, Any]],
                                start_date: date, race_date: date,
                                lang: str = "fr") -> Tuple[bool, str, List[Dict[str, Any]]]:
    """
    Valide les courses intermédiaires

    Args:
        intermediate_races: Liste des courses intermédiaires
        start_date: Date de début du plan
        race_date: Date de la course principale
        lang: Code de langue pour les messages d'erreur

    Returns:
        Tuple (valid, message, validated_races)
    """
    validated_races = []

    for i, race in enumerate(intermediate_races):
        # Valider la date
        race_date_str = race.get("race_date")
        if not race_date_str:
            return False, f"Date manquante pour la course intermédiaire {i+1}", []

        # Convertir en objet date si ce n'est pas déjà le cas
        if isinstance(race_date_str, str):
            try:
                race_date_obj = date.fromisoformat(race_date_str)
            except ValueError:
                return False, f"Format de date invalide pour la course intermédiaire {i+1}", []
        elif isinstance(race_date_str, date):
            race_date_obj = race_date_str
        else:
            return False, f"Type de date invalide pour la course intermédiaire {i+1}", []

        # Vérifier que la date est un dimanche
        if race_date_obj.weekday() != 6:
            return False, translate("race_date_sunday", "validation_error")

        # Vérifier que la date est entre start_date et race_date
        if not (start_date < race_date_obj < race_date):
            return False, translate("intermediate_race_range", "validation_error")

        # Valider le type de course
        race_type_str = race.get("race_type")

        try:
            race_type = RaceType(race_type_str) if race_type_str else None
        except ValueError:
            return False, f"Type de course non reconnu pour la course intermédiaire {i+1}", []

        if race_type == RaceType.OTHER and (race.get("distance") is None or race.get("distance") <= 0):
            return False, f"Distance requise pour la course intermédiaire {i+1} de type 'autre'", []

        # Valider l'allure visée
        target_pace = race.get("target_pace")
        if target_pace is None and "target_pace_str" in race:
            target_pace_str = race.get("target_pace_str")
            if target_pace_str:
                target_pace = parse_pace_string(target_pace_str)

        # Ajouter la course validée
        validated_race = race.copy()
        validated_race["race_date"] = race_date_obj
        if target_pace:
            validated_race["target_pace"] = target_pace

        validated_races.append(validated_race)

    return True, "", validated_races


def validate_user_input(user_input: Dict[str, Any], lang: str = "fr") -> Tuple[bool, str, Dict[str, Any]]:
    """
    Valide toutes les entrées utilisateur

    Args:
        user_input: Dictionnaire des entrées utilisateur
        lang: Code de langue pour les messages d'erreur

    Returns:
        Tuple (valid, message, validated_input)
    """
    validated_input = {}

    # Valider les dates
    start_date = user_input.get("start_date")
    race_date = user_input.get("race_date")

    if not start_date or not race_date:
        return False, "Dates de début et/ou de course manquantes", {}

    valid_dates, message = validate_date_range(start_date, race_date, lang=lang)
    if not valid_dates:
        return False, message, {}

    validated_input["start_date"] = start_date
    validated_input["race_date"] = race_date

    # Valider les informations de course
    race_type = user_input.get("race_type")
    distance = user_input.get("distance")
    target_time = user_input.get("target_time")

    valid_course, message = validate_course_info(race_type, distance, target_time, lang=lang)
    if not valid_course:
        return False, message, {}

    validated_input["race_type"] = race_type
    if distance:
        validated_input["distance"] = distance
    if target_time:
        time_delta = parse_time_string(target_time)
        if time_delta:
            validated_input["target_time"] = time_delta

    # Valider les allures
    pace_5k = user_input.get("pace_5k")
    pace_10k = user_input.get("pace_10k")
    pace_half = user_input.get("pace_half_marathon")
    pace_marathon = user_input.get("pace_marathon")

    if not all([pace_5k, pace_10k, pace_half, pace_marathon]):
        return False, "Toutes les allures doivent être renseignées", {}

    valid_paces, message, paces_dict = validate_paces(pace_5k, pace_10k, pace_half, pace_marathon, lang=lang)
    if not valid_paces:
        return False, message, {}

    validated_input.update(paces_dict)

    # Valider les volumes
    min_volume = user_input.get("min_volume")
    max_volume = user_input.get("max_volume")

    if min_volume is None or max_volume is None:
        return False, "Volumes minimaux et maximaux requis", {}

    valid_volumes, message = validate_volume(min_volume, max_volume, lang=lang)
    if not valid_volumes:
        return False, message, {}

    validated_input["min_volume"] = min_volume
    validated_input["max_volume"] = max_volume

    # Valider le nombre de séances par semaine
    sessions_per_week = user_input.get("sessions_per_week")
    if sessions_per_week is None:
        return False, "Nombre de séances par semaine requis", {}

    valid_sessions, message = validate_sessions_per_week(sessions_per_week, lang=lang)
    if not valid_sessions:
        return False, message, {}

    validated_input["sessions_per_week"] = sessions_per_week

    # Valider les courses intermédiaires (facultatives)
    intermediate_races = user_input.get("intermediate_races", [])

    if intermediate_races:
        valid_races, message, validated_races = validate_intermediate_races(
            intermediate_races, start_date, race_date, lang=lang
        )
        if not valid_races:
            return False, message, {}

        validated_input["intermediate_races"] = validated_races
    else:
        validated_input["intermediate_races"] = []

    return True, "", validated_input