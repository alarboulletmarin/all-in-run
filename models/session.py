"""
Modèle pour représenter une séance d'entraînement.
"""
from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import Enum, auto
from typing import List, Dict, Any, Optional, Tuple

from utils import format_timedelta, format_pace


class SessionType(Enum):
    """Types de séances d'entraînement"""
    LONG_RUN = "Sortie Longue"
    THRESHOLD = "Seuil"
    EF = "Endurance Fondamentale"
    REST = "Repos"
    RACE = "Course"


class TrainingPhase(Enum):
    """Phases d'entraînement"""
    DEVELOPMENT = "Développement"
    SPECIFIC = "Spécifique"
    TAPER = "Affûtage"


class SessionBlock:
    """
    Représente un bloc d'entraînement au sein d'une séance
    (ex: échauffement, bloc actif, retour au calme)
    """
    def __init__(self, distance: float, pace: timedelta, description: str = ""):
        self.distance = distance
        self.pace = pace
        self.description = description

    @property
    def duration(self) -> timedelta:
        """Calcule la durée du bloc en fonction de la distance et de l'allure"""
        seconds = self.pace.total_seconds() * self.distance
        return timedelta(seconds=seconds)

    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'objet en dictionnaire pour sérialisation JSON"""
        return {
            "distance": self.distance,
            "pace": self.pace.total_seconds(),
            "description": self.description
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionBlock':
        """Crée un objet SessionBlock à partir d'un dictionnaire"""
        return cls(
            distance=data["distance"],
            pace=timedelta(seconds=data["pace"]),
            description=data.get("description", "")
        )


@dataclass
class Session:
    """
    Représente une séance d'entraînement.

    Attributes:
        session_date: Date de la séance
        session_type: Type de séance (SL, Seuil, EF, Repos, Course)
        phase: Phase d'entraînement (développement, spécifique, affûtage)
        blocks: Liste des blocs d'activité composant la séance
        description: Description textuelle de la séance
        is_intermediate_race: Indique s'il s'agit d'une course intermédiaire
    """
    session_date: date
    session_type: SessionType
    phase: TrainingPhase
    blocks: List[SessionBlock] = field(default_factory=list)
    description: str = ""
    is_intermediate_race: bool = False

    @property
    def total_distance(self) -> float:
        """Calcule la distance totale de la séance, arrondie au dixième de km"""
        if not self.blocks:
            return 0.0
        total = sum(block.distance for block in self.blocks)
        return round(total, 1)  # Arrondi au dixième

    @property
    def total_duration(self) -> timedelta:
        """Calcule la durée totale de la séance, arrondie à la seconde"""
        if not self.blocks:
            return timedelta(0)
        total_seconds = sum(block.duration.total_seconds() for block in self.blocks)
        return timedelta(seconds=round(total_seconds))  # Arrondi à la seconde

    def get_difficulty_score(self) -> float:
        """
        Calcule un score de difficulté pour la séance
        Plus le score est élevé, plus la séance est difficile
        """
        if self.session_type == SessionType.REST:
            return 0.0

        # Facteurs de pondération par type de séance
        type_factors = {
            SessionType.EF: 1.0,
            SessionType.LONG_RUN: 1.5,
            SessionType.THRESHOLD: 2.0,
            SessionType.RACE: 2.5
        }

        # Score de base: distance * facteur de type
        base_score = self.total_distance * type_factors.get(self.session_type, 1.0)

        # Ajustement en fonction de l'intensité (allure moyenne)
        if self.blocks:
            # Calcul de l'allure moyenne pondérée par la distance
            total_distance = self.total_distance
            if total_distance > 0:
                weighted_pace = sum(
                    block.pace.total_seconds() * (block.distance / total_distance)
                    for block in self.blocks
                )
                # Plus l'allure est rapide (seconds/km petit), plus le score augmente
                intensity_factor = 360 / weighted_pace  # Facteur arbitraire pour normaliser
                return base_score * intensity_factor

        return base_score

    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'objet en dictionnaire pour sérialisation JSON"""
        return {
            "session_date": self.session_date.isoformat(),
            "session_type": self.session_type.value,
            "phase": self.phase.value,
            "blocks": [block.to_dict() for block in self.blocks],
            "description": self.description,
            "is_intermediate_race": self.is_intermediate_race
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Session':
        """Crée un objet Session à partir d'un dictionnaire"""
        session_date = date.fromisoformat(data["session_date"])
        session_type = SessionType(data["session_type"])
        phase = TrainingPhase(data["phase"])
        blocks = [SessionBlock.from_dict(block) for block in data.get("blocks", [])]

        return cls(
            session_date=session_date,
            session_type=session_type,
            phase=phase,
            blocks=blocks,
            description=data.get("description", ""),
            is_intermediate_race=data.get("is_intermediate_race", False)
        )

    @classmethod
    def create_ef_session(cls, session_date: date, phase: TrainingPhase,
                          distance: float, ef_pace: timedelta,
                          description: str = "") -> 'Session':
        """
        Crée une séance d'Endurance Fondamentale (EF)

        Args:
            session_date: Date de la séance
            phase: Phase d'entraînement
            distance: Distance totale en km
            ef_pace: Allure d'endurance fondamentale
            description: Description optionnelle

        Returns:
            Un objet Session configuré pour une séance EF
        """
        # Arrondir la distance au dixième
        distance = round(distance, 1)

        # Créer un seul bloc pour la séance EF
        block = SessionBlock(
            distance=distance,
            pace=ef_pace,
            description=f"Endurance continue à {ef_pace}"
        )

        return cls(
            session_date=session_date,
            session_type=SessionType.EF,
            phase=phase,
            blocks=[block],
            description=description or f"Séance d'endurance fondamentale de {distance} km"
        )

    @classmethod
    def create_long_run_session(cls, session_date: date, phase: TrainingPhase,
                                total_distance: float, ef_pace: timedelta,
                                specific_pace: Optional[timedelta] = None,
                                description: str = "") -> 'Session':
        """
        Crée une séance de Sortie Longue (SL)
        En phase développement et affûtage: 100% à allure EF
        En phase spécifique: 25% échauffement EF, 50% allure spécifique, 25% retour au calme EF

        Args:
            session_date: Date de la séance
            phase: Phase d'entraînement
            total_distance: Distance totale en km
            ef_pace: Allure d'endurance fondamentale
            specific_pace: Allure spécifique (nécessaire en phase spécifique)
            description: Description optionnelle

        Returns:
            Un objet Session configuré pour une sortie longue
        """
        # Arrondir la distance totale au dixième
        total_distance = round(total_distance, 1)
        blocks = []

        if phase == TrainingPhase.SPECIFIC and specific_pace:
            # En phase spécifique: échauffement 25%, bloc actif 50%, retour au calme 25%
            warmup_distance = round(total_distance * 0.25, 1)
            active_distance = round(total_distance * 0.5, 1)
            cooldown_distance = round(total_distance - warmup_distance - active_distance, 1)

            blocks = [
                SessionBlock(
                    distance=warmup_distance,
                    pace=ef_pace,
                    description=f"Échauffement à {ef_pace}"
                ),
                SessionBlock(
                    distance=active_distance,
                    pace=specific_pace,
                    description=f"Bloc principal à {specific_pace}"
                ),
                SessionBlock(
                    distance=cooldown_distance,
                    pace=ef_pace,
                    description=f"Retour au calme à {ef_pace}"
                )
            ]

            desc = description or f"Sortie longue de {total_distance} km avec {active_distance} km à allure spécifique"
        else:
            # En phase développement ou affûtage: 100% à allure EF
            blocks = [
                SessionBlock(
                    distance=total_distance,
                    pace=ef_pace,
                    description=f"Endurance continue à {ef_pace}"
                )
            ]

            desc = description or f"Sortie longue de {total_distance} km à allure endurance fondamentale"

        return cls(
            session_date=session_date,
            session_type=SessionType.LONG_RUN,
            phase=phase,
            blocks=blocks,
            description=desc
        )

    @classmethod
    def create_threshold_session(cls, session_date: date, phase: TrainingPhase,
                                 total_distance: float, ef_pace: timedelta,
                                 threshold_pace: timedelta, interval_minutes: int,
                                 description: str = "") -> 'Session':
        """
        Crée une séance de Seuil
        Structure: 25% échauffement EF, 50% alternance (x min seuil / x min EF), 25% retour au calme EF

        Args:
            session_date: Date de la séance
            phase: Phase d'entraînement
            total_distance: Distance totale en km
            ef_pace: Allure d'endurance fondamentale
            threshold_pace: Allure de seuil
            interval_minutes: Durée des intervalles en minutes (généralement 1, 2 ou 3)
            description: Description optionnelle

        Returns:
            Un objet Session configuré pour une séance de seuil
        """
        # Arrondir la distance totale au dixième
        total_distance = round(total_distance, 1)

        # Calcul des distances de chaque partie
        warmup_distance = round(total_distance * 0.25, 1)
        active_total_distance = round(total_distance * 0.5, 1)
        cooldown_distance = round(total_distance - warmup_distance - active_total_distance, 1)

        # Calcul du nombre de répétitions nécessaires pour couvrir active_total_distance
        # Distance par minute à allure seuil
        distance_per_min_threshold = 1000 / threshold_pace.total_seconds() * 60 / 1000  # km/min
        # Distance par minute à allure EF
        distance_per_min_ef = 1000 / ef_pace.total_seconds() * 60 / 1000  # km/min

        # Distance par répétition (x min seuil + x min EF)
        distance_per_rep = interval_minutes * (distance_per_min_threshold + distance_per_min_ef)

        # Nombre de répétitions arrondi
        num_reps = max(1, round(active_total_distance / distance_per_rep))

        # Recalcul des distances exactes pour chaque répétition
        threshold_distance_per_rep = round(interval_minutes * distance_per_min_threshold, 1)
        ef_distance_per_rep = round(interval_minutes * distance_per_min_ef, 1)

        # Création des blocs
        blocks = [
            SessionBlock(
                distance=warmup_distance,
                pace=ef_pace,
                description=f"Échauffement à {ef_pace}/km"
            )
        ]

        # Ajouter les répétitions
        for i in range(num_reps):
            blocks.append(
                SessionBlock(
                    distance=threshold_distance_per_rep,
                    pace=threshold_pace,
                    description=f"Intervalle {i+1}/{num_reps} à {threshold_pace}/km"
                )
            )
            blocks.append(
                SessionBlock(
                    distance=ef_distance_per_rep,
                    pace=ef_pace,
                    description=f"Récupération {i+1}/{num_reps} à {ef_pace}/km"
                )
            )

        # Ajouter le retour au calme
        blocks.append(
            SessionBlock(
                distance=cooldown_distance,
                pace=ef_pace,
                description=f"Retour au calme à {ef_pace}/km"
            )
        )

        # Calculer les temps approximatifs pour chaque phase
        warmup_time = format_timedelta(timedelta(seconds=warmup_distance * ef_pace.total_seconds()), "ms")
        interval_block_time = format_timedelta(timedelta(seconds=num_reps * 2 * interval_minutes * 60), "ms")
        cooldown_time = format_timedelta(timedelta(seconds=cooldown_distance * ef_pace.total_seconds()), "ms")

        # Ajuster la description avec les informations de temps
        desc = description or (
            f"Séance de seuil: {warmup_time} d'échauffement à {format_pace(ef_pace)}, "
            f"{num_reps}×({interval_minutes}' à {format_pace(threshold_pace)} / {interval_minutes}' à {format_pace(ef_pace)}), "
            f"{cooldown_time} de retour au calme à {format_pace(ef_pace)}"
        )

        return cls(
            session_date=session_date,
            session_type=SessionType.THRESHOLD,
            phase=phase,
            blocks=blocks,
            description=desc
        )

    @classmethod
    def create_rest_session(cls, session_date: date, phase: TrainingPhase) -> 'Session':
        """
        Crée une séance de repos

        Args:
            session_date: Date de la séance
            phase: Phase d'entraînement

        Returns:
            Un objet Session configuré pour une séance de repos
        """
        return cls(
            session_date=session_date,
            session_type=SessionType.REST,
            phase=phase,
            blocks=[],
            description="Journée de repos"
        )

    @classmethod
    def create_race_session(cls, session_date: date, phase: TrainingPhase,
                            race_distance: float, race_pace: timedelta,
                            description: str = "", is_intermediate: bool = False) -> 'Session':
        """
        Crée une séance de course (principale ou intermédiaire)

        Args:
            session_date: Date de la séance
            phase: Phase d'entraînement
            race_distance: Distance de la course en km
            race_pace: Allure visée pour la course
            description: Description optionnelle
            is_intermediate: Indique s'il s'agit d'une course intermédiaire

        Returns:
            Un objet Session configuré pour une course
        """
        # Arrondir la distance au dixième
        race_distance = round(race_distance, 1)

        block = SessionBlock(
            distance=race_distance,
            pace=race_pace,
            description=f"Course à {race_pace}"
        )

        desc = description or f"Course de {race_distance} km à {race_pace}"

        return cls(
            session_date=session_date,
            session_type=SessionType.RACE,
            phase=phase,
            blocks=[block],
            description=desc,
            is_intermediate_race=is_intermediate
        )