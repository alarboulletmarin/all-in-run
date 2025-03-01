"""
Utilitaires pour la gestion des dates.
"""
from datetime import date, datetime, timedelta
from typing import List, Tuple, Optional, Generator
from config.languages import DAYS_TRANSLATIONS, MONTHS_TRANSLATIONS


def get_next_monday(from_date: date) -> date:
    """
    Obtient le prochain lundi à partir d'une date donnée

    Args:
        from_date: Date de départ

    Returns:
        Date du prochain lundi (ou la date elle-même si c'est un lundi)
    """
    # 0 = lundi, 6 = dimanche
    days_until_monday = (0 - from_date.weekday()) % 7
    if days_until_monday == 0 and from_date.weekday() == 0:
        # C'est déjà un lundi
        return from_date
    return from_date + timedelta(days=days_until_monday)


def get_sunday(from_date: date) -> date:
    """
    Obtient le dimanche de la semaine d'une date donnée

    Args:
        from_date: Date de départ

    Returns:
        Date du dimanche de la semaine (ou la date elle-même si c'est un dimanche)
    """
    # 0 = lundi, 6 = dimanche
    days_until_sunday = (6 - from_date.weekday()) % 7
    if days_until_sunday == 0 and from_date.weekday() == 6:
        # C'est déjà un dimanche
        return from_date
    return from_date + timedelta(days=days_until_sunday)


def get_first_day_of_week(date_in_week: date) -> date:
    """
    Obtient le premier jour (lundi) de la semaine d'une date donnée

    Args:
        date_in_week: Date dans la semaine

    Returns:
        Date du lundi de la semaine
    """
    return date_in_week - timedelta(days=date_in_week.weekday())


def get_days_between(start_date: date, end_date: date) -> List[date]:
    """
    Obtient la liste des dates entre deux dates (incluses)

    Args:
        start_date: Date de début
        end_date: Date de fin

    Returns:
        Liste des dates entre start_date et end_date (incluses)
    """
    days = []
    current_date = start_date
    while current_date <= end_date:
        days.append(current_date)
        current_date += timedelta(days=1)
    return days


def get_weeks_between(start_date: date, end_date: date) -> List[Tuple[date, date]]:
    """
    Obtient la liste des semaines entre deux dates
    Chaque semaine est représentée par un tuple (lundi, dimanche)

    Args:
        start_date: Date de début
        end_date: Date de fin

    Returns:
        Liste des semaines entre start_date et end_date
    """
    # S'assurer que start_date est un lundi
    start_monday = get_first_day_of_week(start_date)

    weeks = []
    current_monday = start_monday

    while current_monday <= end_date:
        current_sunday = current_monday + timedelta(days=6)
        weeks.append((current_monday, current_sunday))
        current_monday += timedelta(days=7)

    return weeks


def get_week_number(target_date: date, start_date: date) -> int:
    """
    Calcule le numéro de la semaine d'une date par rapport à une date de début

    Args:
        target_date: Date cible
        start_date: Date de référence (début)

    Returns:
        Numéro de semaine (0-indexed)
    """
    # S'assurer que start_date est un lundi
    start_monday = get_first_day_of_week(start_date)

    # Calculer le nombre de jours entre les deux dates
    days_diff = (target_date - start_monday).days

    # Convertir en semaines (0-indexed)
    return days_diff // 7


def get_date_from_week_and_day(start_date: date, week_num: int, weekday: int) -> date:
    """
    Obtient une date à partir d'un numéro de semaine et d'un jour de la semaine

    Args:
        start_date: Date de début (référence)
        week_num: Numéro de la semaine (0-indexed)
        weekday: Jour de la semaine (0 = lundi, 6 = dimanche)

    Returns:
        Date correspondante
    """
    # S'assurer que start_date est un lundi
    start_monday = get_first_day_of_week(start_date)

    # Calculer la date du lundi de la semaine demandée
    week_monday = start_monday + timedelta(days=week_num * 7)

    # Ajouter le nombre de jours correspondant au jour de la semaine demandé
    return week_monday + timedelta(days=weekday)


def format_date(d: date, lang: str = "fr", include_day_name: bool = True) -> str:
    """
    Formate une date selon la langue spécifiée

    Args:
        d: Date à formater
        lang: Code de langue
        include_day_name: Indique si le nom du jour doit être inclus

    Returns:
        Date formatée selon la langue
    """
    day_name = DAYS_TRANSLATIONS.get(lang, {}).get(d.weekday(), "")
    month_name = MONTHS_TRANSLATIONS.get(lang, {}).get(d.month, "")

    if lang == "en":
        if include_day_name:
            return f"{day_name}, {month_name} {d.day}, {d.year}"
        return f"{month_name} {d.day}, {d.year}"
    elif lang == "fr":
        if include_day_name:
            return f"{day_name} {d.day} {month_name} {d.year}"
        return f"{d.day} {month_name} {d.year}"
    elif lang == "es":
        if include_day_name:
            return f"{day_name}, {d.day} de {month_name} de {d.year}"
        return f"{d.day} de {month_name} de {d.year}"

    # Format par défaut
    return d.strftime("%d/%m/%Y")


def get_date_range_for_month(year: int, month: int) -> Tuple[date, date]:
    """
    Obtient la plage de dates pour un mois donné

    Args:
        year: Année
        month: Mois (1-12)

    Returns:
        Tuple (premier jour du mois, dernier jour du mois)
    """
    first_day = date(year, month, 1)

    # Calculer le dernier jour du mois
    if month == 12:
        last_day = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day = date(year, month + 1, 1) - timedelta(days=1)

    return first_day, last_day


def days_between(d1: date, d2: date) -> int:
    """
    Calcule le nombre de jours entre deux dates

    Args:
        d1: Première date
        d2: Deuxième date

    Returns:
        Nombre de jours entre d1 et d2
    """
    return abs((d2 - d1).days)


def weeks_between(d1: date, d2: date) -> int:
    """
    Calcule le nombre de semaines entre deux dates

    Args:
        d1: Première date
        d2: Deuxième date

    Returns:
        Nombre de semaines entre d1 et d2
    """
    return days_between(d1, d2) // 7


def yield_month_calendar(year: int, month: int) -> Generator[List[Optional[date]], None, None]:
    """
    Génère un calendrier mensuel sous forme de liste de semaines
    Chaque semaine est une liste de 7 dates (lundi à dimanche)
    Les jours hors du mois sont représentés par None

    Args:
        year: Année
        month: Mois (1-12)

    Yields:
        Liste de 7 dates ou None pour chaque semaine du mois
    """
    first_day, last_day = get_date_range_for_month(year, month)

    # Trouver le premier lundi du calendrier (peut être dans le mois précédent)
    calendar_start = get_first_day_of_week(first_day)

    # Trouver le dernier dimanche du calendrier (peut être dans le mois suivant)
    last_day_weekday = last_day.weekday()
    calendar_end = last_day + timedelta(days=6 - last_day_weekday)

    # Générer les semaines
    current_date = calendar_start
    week = []

    while current_date <= calendar_end:
        # Si c'est un jour en dehors du mois, ajouter None
        if current_date.month != month:
            week.append(None)
        else:
            week.append(current_date)

        # Passer au jour suivant
        current_date += timedelta(days=1)

        # Si c'est dimanche, on a complété une semaine
        if current_date.weekday() == 0:
            yield week
            week = []