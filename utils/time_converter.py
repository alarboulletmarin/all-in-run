from datetime import timedelta
from typing import Optional, Union
import re


def parse_time_string(time_str: str) -> Optional[timedelta]:
    """
    Convertit une chaîne de temps en timedelta.
    Formats supportés:
    - hh:mm:ss (ex: 01:30:00 pour 1h30min)
    - mm:ss (ex: 05:30 pour 5min30s)

    Args:
        time_str: Chaîne de temps à convertir

    Returns:
        timedelta ou None si la conversion a échoué
    """
    if not isinstance(time_str, str):
        return None

    time_str = time_str.strip()

    # Format hh:mm:ss
    pattern_hhmmss = re.compile(r"^(\d{1,2}):(\d{1,2}):(\d{1,2})$")
    match_hhmmss = pattern_hhmmss.match(time_str)
    if match_hhmmss:
        hours, minutes, seconds = map(int, match_hhmmss.groups())
        return timedelta(hours=hours, minutes=minutes, seconds=seconds)

    # Format mm:ss
    pattern_mmss = re.compile(r"^(\d{1,2}):(\d{1,2})$")
    match_mmss = pattern_mmss.match(time_str)
    if match_mmss:
        minutes, seconds = map(int, match_mmss.groups())
        return timedelta(minutes=minutes, seconds=seconds)

    return None


def format_timedelta(td: timedelta, format_type: str = "hms") -> str:
    """
    Formate un timedelta en chaîne de caractères selon le format spécifié

    Args:
        td: Timedelta à formater
        format_type: Format souhaité ("hms" = hh:mm:ss, "ms" = mm:ss, "hms_text" = 1h 30min 45s)

    Returns:
        Chaîne formatée
    """
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    if format_type == "hms":
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    elif format_type == "ms":
        if hours > 0:
            # Convertir les heures en minutes
            minutes += hours * 60
        return f"{minutes:02d}:{seconds:02d}"
    elif format_type == "hms_text":
        components = []
        if hours > 0:
            components.append(f"{hours}h")
        if minutes > 0 or not components:
            components.append(f"{minutes:02d}min")
        if seconds > 0 or not components:
            components.append(f"{seconds:02d}s")
        return " ".join(components)
    else:
        # Format par défaut
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def format_pace(pace: timedelta) -> str:
    """
    Formate une allure (minutes par kilomètre) en chaîne de caractères (mm:ss/km)

    Args:
        pace: Allure en timedelta

    Returns:
        Chaîne d'allure formatée
    """
    total_seconds = int(pace.total_seconds())
    minutes, seconds = divmod(total_seconds, 60)
    return f"{minutes:02d}:{seconds:02d}/km"


def parse_pace_string(pace_str: Union[str, timedelta]) -> Optional[timedelta]:
    """
    Convertit une chaîne d'allure en timedelta
    Format supporté: mm:ss ou mm:ss/km

    Args:
        pace_str: Chaîne d'allure à convertir ou timedelta

    Returns:
        timedelta ou None si la conversion a échoué
    """
    # Si pace_str est déjà un timedelta, le retourner directement
    if isinstance(pace_str, timedelta):
        return pace_str

    # S'assurer que l'entrée est une chaîne
    if not isinstance(pace_str, str):
        return None

    # Supprimer "/km" si présent et les espaces
    pace_str = pace_str.strip().replace("/km", "").strip()

    # Format mm:ss
    pattern_mmss = re.compile(r"^(\d{1,2}):(\d{1,2})$")
    match_mmss = pattern_mmss.match(pace_str)
    if match_mmss:
        minutes, seconds = map(int, match_mmss.groups())
        return timedelta(minutes=minutes, seconds=seconds)

    return None


def calculate_time_from_distance_and_pace(distance: float, pace: timedelta) -> timedelta:
    """
    Calcule le temps total à partir d'une distance et d'une allure

    Args:
        distance: Distance en kilomètres
        pace: Allure en minutes par kilomètre (timedelta)

    Returns:
        Temps total (timedelta)
    """
    total_seconds = pace.total_seconds() * distance
    return timedelta(seconds=round(total_seconds))


def calculate_pace_from_distance_and_time(distance: float, time: timedelta) -> timedelta:
    """
    Calcule l'allure à partir d'une distance et d'un temps

    Args:
        distance: Distance en kilomètres
        time: Temps total (timedelta)

    Returns:
        Allure en minutes par kilomètre (timedelta)
    """
    if distance <= 0:
        raise ValueError("La distance doit être positive")

    # Allure = temps / distance
    seconds_per_km = time.total_seconds() / distance
    return timedelta(seconds=seconds_per_km)


def add_time_to_pace(pace: timedelta, seconds_to_add: int) -> timedelta:
    """
    Ajoute des secondes à une allure

    Args:
        pace: Allure originale (timedelta)
        seconds_to_add: Nombre de secondes à ajouter

    Returns:
        Nouvelle allure (timedelta)
    """
    new_seconds = pace.total_seconds() + seconds_to_add
    return timedelta(seconds=new_seconds)


def format_duration_for_calendar(duration: timedelta) -> str:
    """
    Formate une durée pour l'affichage dans un calendrier
    Si < 1h: format mm:ss, sinon: format hh:mm

    Args:
        duration: Durée à formater

    Returns:
        Chaîne formatée
    """
    total_seconds = int(duration.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    if hours == 0:
        return f"{minutes:02d}:{seconds:02d}"
    else:
        return f"{hours:02d}:{minutes:02d}"