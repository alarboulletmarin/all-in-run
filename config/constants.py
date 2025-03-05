"""
Constantes utilisées dans l'application All-in-Run.
"""

DATE_FORMAT = "DD/MM/YYYY"  # Format d'affichage des dates

# Constantes temporelles
MIN_WEEKS_BEFORE_RACE = 12  # Nombre minimal de semaines entre début et course
MIN_TAPER_WEEKS = 4  # Nombre minimal de semaines d'affûtage

# Constantes de répartition
TAPER_PHASE_RATIO = 0.20  # Pourcentage de la durée totale pour l'affûtage
DEVELOPMENT_SPECIFIC_RATIO = 4/3  # Ratio entre développement et spécifique (4:3)

# Constantes de volume
VOLUME_REDUCTION_RACE_WEEK = 0.20  # Réduction de volume semaine de course intermédiaire
TAPER_FINAL_WEEK_RATIO = 0.50  # Volume de la dernière semaine par rapport au min
CHARGE_DISCHARGE_PATTERN = [1, 1, 0]  # Schéma de charge/décharge (1=charge, 0=décharge)
DISCHARGE_REDUCTION = 0.20  # Réduction pour une semaine de décharge (-20%)

# Répartition des types de séances par phase
LONG_RUN_VOLUME_RATIO = 0.40  # Ratio de la sortie longue par rapport au volume hebdo
THRESHOLD_VOLUME_RATIO = 0.25  # Ratio de la séance seuil par rapport au volume hebdo
EF_VOLUME_RATIO = 0.35  # Ratio de l'endurance fondamentale (reste)

# Répartition des blocs dans les séances
WARMUP_RATIO = 0.25  # Ratio d'échauffement dans une séance structurée
ACTIVE_BLOCK_RATIO = 0.50  # Ratio du bloc actif dans une séance structurée
COOLDOWN_RATIO = 0.25  # Ratio de retour au calme dans une séance structurée

# Configuration des jours de séances
DEFAULT_LONG_RUN_DAY = 6  # Dimanche (0 = lundi, 6 = dimanche)
DEFAULT_THRESHOLD_DAY = 3  # Jeudi
REST_DAY_PRIORITY = [0, 4, 1, 5]  # Lundi, vendredi, mardi, samedi

# Limites par défaut
DEFAULT_MIN_VOLUME = 20.0  # Volume minimal par défaut (km)
DEFAULT_MAX_VOLUME = 60.0  # Volume maximal par défaut (km)
DEFAULT_SESSIONS_PER_WEEK = 4  # Nombre de séances par semaine par défaut
MIN_SESSIONS_PER_WEEK = 3  # Nombre minimal de séances par semaine
MAX_SESSIONS_PER_WEEK = 7  # Nombre maximal de séances par semaine

# Constantes d'arrondissement
DISTANCE_PRECISION = 0.1  # Arrondi des distances au dixième de km

# Paramètres des séances de seuil
THRESHOLD_INTERVAL_MINUTES = {
    "10K": 1,  # 1 minute pour le seuil 10K
    "half_marathon": [2, 3],  # Alterner 2 et 3 minutes pour le seuil semi
    "marathon": [2, 3],  # Alterner 2 et 3 minutes pour le seuil marathon
    "other": [2, 3]  # Alterner 2 et 3 minutes pour les autres types
}

# Configuration des exports
PDF_PAGE_SIZE = "A4"
PDF_ORIENTATION = "portrait"