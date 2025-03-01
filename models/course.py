"""
Modèle pour représenter une course (principale ou intermédiaire).
"""
from dataclasses import dataclass
from datetime import date, timedelta
from enum import Enum, auto
from typing import Optional, Dict, Any


class RaceType(Enum):
    """Types de courses disponibles"""
    TEN_K = "10K"
    HALF_MARATHON = "semi-marathon"
    MARATHON = "marathon"
    OTHER = "autre"


@dataclass
class Course:
    """
    Représente une course (principale ou intermédiaire).

    Attributes:
        race_date: Date de la course (obligatoirement un dimanche)
        race_type: Type de course (10K, semi-marathon, marathon, autre)
        distance: Distance en km (obligatoire si race_type est OTHER)
        target_time: Temps cible au format timedelta (obligatoire si race_type est OTHER)
        target_pace: Allure visée en min/km (timedelta)
        is_main_race: Indique s'il s'agit de la course principale
    """
    race_date: date
    race_type: RaceType
    distance: Optional[float] = None
    target_time: Optional[timedelta] = None
    target_pace: Optional[timedelta] = None
    is_main_race: bool = False

    def __post_init__(self):
        """Validation après initialisation"""
        # Vérifier que la date est un dimanche
        if self.race_date.weekday() != 6:  # 6 = dimanche
            raise ValueError("La date de course doit être un dimanche")

        # Vérifier que distance et target_time sont renseignés si race_type est OTHER
        if self.race_type == RaceType.OTHER:
            if self.distance is None:
                raise ValueError("La distance est obligatoire pour les courses de type 'autre'")
            if self.target_time is None and self.is_main_race:
                raise ValueError("Le temps cible est obligatoire pour les courses principales de type 'autre'")

        # Si target_time est fourni, calculer l'allure cible
        if self.target_time is not None and self.distance is not None and self.target_pace is None:
            # Allure = temps total / distance
            self.target_pace = timedelta(seconds=self.target_time.total_seconds() / self.distance)

    @property
    def get_standard_distance(self) -> float:
        """Retourne la distance standard selon le type de course"""
        if self.race_type == RaceType.TEN_K:
            return 10.0
        elif self.race_type == RaceType.HALF_MARATHON:
            return 21.1
        elif self.race_type == RaceType.MARATHON:
            return 42.2
        else:
            return self.distance if self.distance is not None else 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'objet en dictionnaire pour sérialisation JSON"""
        return {
            "race_date": self.race_date.isoformat(),
            "race_type": self.race_type.value,
            "distance": self.distance,
            "target_time": self.target_time.total_seconds() if self.target_time else None,
            "target_pace": self.target_pace.total_seconds() if self.target_pace else None,
            "is_main_race": self.is_main_race
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Course':
        """Crée un objet Course à partir d'un dictionnaire"""
        # Conversion des types
        race_date = date.fromisoformat(data["race_date"])
        race_type = RaceType(data["race_type"])
        target_time = timedelta(seconds=data["target_time"]) if data.get("target_time") else None
        target_pace = timedelta(seconds=data["target_pace"]) if data.get("target_pace") else None

        return cls(
            race_date=race_date,
            race_type=race_type,
            distance=data.get("distance"),
            target_time=target_time,
            target_pace=target_pace,
            is_main_race=data.get("is_main_race", False)
        )