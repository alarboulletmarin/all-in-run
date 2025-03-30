# Format d'affichage des dates dans l'interface utilisateur
DATE_FORMAT = "DD/MM/YYYY"

# Paramètres fondamentaux de génération des plans
MIN_WEEKS_BEFORE_RACE = 12  # Durée minimale requise pour un plan d'entraînement complet
MIN_TAPER_WEEKS = 4         # Durée minimale de la phase d'affûtage avant une course

# Coefficients de calcul des phases d'entraînement
TAPER_PHASE_RATIO = 0.20       # Portion de la durée totale consacrée à l'affûtage
DEVELOPMENT_SPECIFIC_RATIO = 4/3  # Ratio entre phase de développement et phase spécifique

# Paramètres de modulation du volume d'entraînement
VOLUME_REDUCTION_RACE_WEEK = 0.20  # Réduction de volume pour une semaine incluant une course
TAPER_FINAL_WEEK_RATIO = 0.50      # Volume de la dernière semaine par rapport au volume minimal
CHARGE_DISCHARGE_PATTERN = [1, 1, 0]  # Séquence charge/décharge (1=charge, 0=décharge)
DISCHARGE_REDUCTION = 0.20           # Facteur de réduction pour une semaine de décharge

# Distribution du volume entre les différents types de séances
LONG_RUN_VOLUME_RATIO = 0.40   # Proportion du volume hebdomadaire pour la sortie longue
THRESHOLD_VOLUME_RATIO = 0.25  # Proportion du volume hebdomadaire pour la séance seuil
EF_VOLUME_RATIO = 0.35         # Proportion du volume hebdomadaire pour l'endurance fondamentale

# Structure interne des séances d'entraînement
WARMUP_RATIO = 0.25        # Proportion d'échauffement dans une séance structurée
ACTIVE_BLOCK_RATIO = 0.50  # Proportion du bloc principal de travail
COOLDOWN_RATIO = 0.25      # Proportion de retour au calme

# Planification hebdomadaire par défaut
DEFAULT_LONG_RUN_DAY = 6   # Jour privilégié pour la sortie longue (0=lundi, 6=dimanche)
DEFAULT_THRESHOLD_DAY = 3  # Jour privilégié pour la séance de seuil
REST_DAY_PRIORITY = [0, 4, 1, 5]  # Priorité des jours de repos (lundi, vendredi, mardi, samedi)

# Valeurs par défaut pour les nouveaux plans
DEFAULT_MIN_VOLUME = 20.0  # Volume minimal hebdomadaire en km
DEFAULT_MAX_VOLUME = 60.0  # Volume maximal hebdomadaire en km
DEFAULT_SESSIONS_PER_WEEK = 4  # Fréquence de course recommandée
MIN_SESSIONS_PER_WEEK = 3      # Minimum de séances pour un plan valide
MAX_SESSIONS_PER_WEEK = 7      # Maximum de séances par semaine

# Précision des calculs et affichages
DISTANCE_PRECISION = 0.1  # Précision des distances (arrondi au dixième de km)

# Configuration des intervalles de seuil selon l'objectif de course
THRESHOLD_INTERVAL_MINUTES = {
    "10K": 1,              # Intervalles courts pour le 10K
    "half_marathon": [2, 3],  # Alternance d'intervalles moyens pour le semi
    "marathon": [2, 3],       # Intervalles similaires pour le marathon
    "other": [2, 3]           # Configuration générique pour les autres distances
}

# Paramètres d'export des documents
PDF_PAGE_SIZE = "A4"
PDF_ORIENTATION = "portrait"