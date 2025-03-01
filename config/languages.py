"""
Configuration des langues disponibles pour l'application All-in-Run.
"""
from typing import Dict, List, Tuple

# Langues disponibles - Tuple (code, nom affiché)
AVAILABLE_LANGUAGES: List[Tuple[str, str]] = [
    ("fr", "Français"),
    ("en", "English"),
    ("es", "Español")
]

# Langue par défaut
DEFAULT_LANGUAGE = "fr"

# Mappings des jours pour l'affichage dans différentes langues
DAYS_TRANSLATIONS: Dict[str, Dict[int, str]] = {
    "fr": {
        0: "Lundi", 1: "Mardi", 2: "Mercredi", 3: "Jeudi",
        4: "Vendredi", 5: "Samedi", 6: "Dimanche"
    },
    "en": {
        0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday",
        4: "Friday", 5: "Saturday", 6: "Sunday"
    },
    "es": {
        0: "Lunes", 1: "Martes", 2: "Miércoles", 3: "Jueves",
        4: "Viernes", 5: "Sábado", 6: "Domingo"
    }
}

# Mappings des mois pour l'affichage dans différentes langues
MONTHS_TRANSLATIONS: Dict[str, Dict[int, str]] = {
    "fr": {
        1: "Janvier", 2: "Février", 3: "Mars", 4: "Avril", 5: "Mai", 6: "Juin",
        7: "Juillet", 8: "Août", 9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Décembre"
    },
    "en": {
        1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
        7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"
    },
    "es": {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
        7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
    }
}

# Mappings des types de séances
SESSION_TYPE_TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "fr": {
        "Sortie Longue": "Sortie Longue",
        "Seuil": "Seuil",
        "Endurance Fondamentale": "Endurance Fondamentale",
        "Repos": "Repos",
        "Course": "Course"
    },
    "en": {
        "Sortie Longue": "Long Run",
        "Seuil": "Threshold",
        "Endurance Fondamentale": "Easy Run",
        "Repos": "Rest",
        "Course": "Race"
    },
    "es": {
        "Sortie Longue": "Carrera Larga",
        "Seuil": "Umbral",
        "Endurance Fondamentale": "Resistencia Básica",
        "Repos": "Descanso",
        "Course": "Carrera"
    }
}

# Mappings des phases d'entraînement
PHASE_TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "fr": {
        "Développement": "Développement",
        "Spécifique": "Spécifique",
        "Affûtage": "Affûtage"
    },
    "en": {
        "Développement": "Development",
        "Spécifique": "Specific",
        "Affûtage": "Taper"
    },
    "es": {
        "Développement": "Desarrollo",
        "Spécifique": "Específico",
        "Affûtage": "Afinamiento"
    }
}

# Mappings des unités pour l'affichage dans différentes langues
UNITS_TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "fr": {
        "km": "km",
        "min_per_km": "min/km",
        "hour": "heure",
        "hours": "heures",
        "minute": "minute",
        "minutes": "minutes",
        "second": "seconde",
        "seconds": "secondes"
    },
    "en": {
        "km": "km",
        "min_per_km": "min/km",
        "hour": "hour",
        "hours": "hours",
        "minute": "minute",
        "minutes": "minutes",
        "second": "second",
        "seconds": "seconds"
    },
    "es": {
        "km": "km",
        "min_per_km": "min/km",
        "hour": "hora",
        "hours": "horas",
        "minute": "minuto",
        "minutes": "minutos",
        "second": "segundo",
        "seconds": "segundos"
    }
}

# Mappings des messages d'erreur de validation
VALIDATION_ERROR_TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "fr": {
        "start_date_monday": "La date de début doit être un lundi.",
        "race_date_sunday": "La date de course doit être un dimanche.",
        "min_weeks": "La préparation doit durer au moins 12 semaines.",
        "pace_order": "Les allures doivent respecter l'ordre: 5K < 10K < Semi < Marathon.",
        "volume_order": "Le volume maximal doit être supérieur au volume minimal.",
        "sessions_range": "Le nombre de séances par semaine doit être entre 3 et 7."
    },
    "en": {
        "start_date_monday": "Start date must be a Monday.",
        "race_date_sunday": "Race date must be a Sunday.",
        "min_weeks": "Training plan must be at least 12 weeks long.",
        "pace_order": "Paces must respect the order: 5K < 10K < Half < Marathon.",
        "volume_order": "Maximum volume must be greater than minimum volume.",
        "sessions_range": "Number of sessions per week must be between 3 and 7."
    },
    "es": {
        "start_date_monday": "La fecha de inicio debe ser un lunes.",
        "race_date_sunday": "La fecha de la carrera debe ser un domingo.",
        "min_weeks": "La preparación debe durar al menos 12 semanas.",
        "pace_order": "Los ritmos deben respetar el orden: 5K < 10K < Medio < Maratón.",
        "volume_order": "El volumen máximo debe ser superior al volumen mínimo.",
        "sessions_range": "El número de sesiones por semana debe estar entre 3 y 7."
    }
}