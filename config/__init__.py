# Importation des configurations et constantes
from .constants import *
from .settings import settings

# Importation des ressources linguistiques
from .languages import (
    AVAILABLE_LANGUAGES,
    DEFAULT_LANGUAGE,
    DAYS_TRANSLATIONS,
    MONTHS_TRANSLATIONS,
    SESSION_TYPE_TRANSLATIONS,
    PHASE_TRANSLATIONS,
    UNITS_TRANSLATIONS,
    VALIDATION_ERROR_TRANSLATIONS
)

# Liste complète des symboles exportés par le module
__all__ = [
    # Configuration dynamique
    'settings',
    
    # Ressources linguistiques
    'AVAILABLE_LANGUAGES',
    'DEFAULT_LANGUAGE',
    'DAYS_TRANSLATIONS',
    'MONTHS_TRANSLATIONS',
    'SESSION_TYPE_TRANSLATIONS',
    'PHASE_TRANSLATIONS',
    'UNITS_TRANSLATIONS',
    'VALIDATION_ERROR_TRANSLATIONS',
    
    # Constantes de formatage
    'DATE_FORMAT',
    
    # Constantes de génération de plan
    'MIN_WEEKS_BEFORE_RACE',
    'MIN_TAPER_WEEKS',
    'TAPER_PHASE_RATIO',
    'DEVELOPMENT_SPECIFIC_RATIO',
    
    # Constantes de volume et intensité
    'VOLUME_REDUCTION_RACE_WEEK',
    'TAPER_FINAL_WEEK_RATIO',
    'CHARGE_DISCHARGE_PATTERN',
    'DISCHARGE_REDUCTION',
    'LONG_RUN_VOLUME_RATIO',
    'THRESHOLD_VOLUME_RATIO',
    'EF_VOLUME_RATIO',
    
    # Structure des séances
    'WARMUP_RATIO',
    'ACTIVE_BLOCK_RATIO',
    'COOLDOWN_RATIO',
    
    # Organisation hebdomadaire
    'DEFAULT_LONG_RUN_DAY',
    'DEFAULT_THRESHOLD_DAY',
    'REST_DAY_PRIORITY',
    
    # Paramètres par défaut
    'DEFAULT_MIN_VOLUME',
    'DEFAULT_MAX_VOLUME',
    'DEFAULT_SESSIONS_PER_WEEK',
    'MIN_SESSIONS_PER_WEEK',
    'MAX_SESSIONS_PER_WEEK',
    
    # Constantes techniques
    'DISTANCE_PRECISION',
    'THRESHOLD_INTERVAL_MINUTES',
    
    # Format d'exports
    'PDF_PAGE_SIZE',
    'PDF_ORIENTATION'
]