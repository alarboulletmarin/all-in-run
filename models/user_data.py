"""
Modèle pour les données utilisateur nécessaires à la génération du plan d'entraînement.
"""
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Dict, Any, Optional
from .course import Course, RaceType


@dataclass
class UserData:
    """
    Données utilisateur pour la génération du plan d'entraînement.

    Attributes:
        start_date: Date de début du plan (obligatoirement un lundi)
        main_race: Course principale (objectif)
        pace_5k: Allure sur 5km (min/km)
        pace_10k: Allure sur 10km (min/km)
        pace_half_marathon: Allure sur semi-marathon (min/km)
        pace_marathon: Allure sur marathon (min/km)
        sessions_per_week: Nombre de séances par semaine (3-7)
        min_volume: Volume hebdomadaire minimal (km)
        max_volume: Volume hebdomadaire maximal (km)
        intermediate_races: Liste des courses intermédiaires
    """
    start_date: date
    main_race: Course
    pace_5k: timedelta
    pace_10k: timedelta
    pace_half_marathon: timedelta
    pace_marathon: timedelta
    sessions_per_week: int
    min_volume: float
    max_volume: float
    intermediate_races: List[Course] = field(default_factory=list)

    def __post_init__(self):
        """Validation après initialisation"""
        # Vérifier que la date de début est un lundi
        if self.start_date.weekday() != 0:  # 0 = lundi
            raise ValueError("La date de début doit être un lundi")

        # Vérifier que la course principale est bien marquée comme telle
        self.main_race.is_main_race = True

        # Vérifier le nombre de semaines minimal entre début et course (12 semaines)
        weeks_diff = (self.main_race.race_date - self.start_date).days // 7
        if weeks_diff < 12:
            raise ValueError("Il doit y avoir au moins 12 semaines entre le début du plan et la course principale")

        # Vérifier l'ordre des allures (5k < 10k < semi < marathon)
        if not (self.pace_5k < self.pace_10k < self.pace_half_marathon < self.pace_marathon):
            raise ValueError("Les allures doivent respecter l'ordre: 5K < 10K < Semi < Marathon")

        # Vérifier que le volume max est supérieur au volume min
        if self.min_volume > self.max_volume:
            raise ValueError("Le volume maximal doit être supérieur au volume minimal")

        # Vérifier que le nombre de séances est entre 3 et 7
        if not (3 <= self.sessions_per_week <= 7):
            raise ValueError("Le nombre de séances par semaine doit être compris entre 3 et 7")

        # Vérifier que les courses intermédiaires sont entre start_date et main_race.race_date
        for race in self.intermediate_races:
            if not (self.start_date < race.race_date < self.main_race.race_date):
                raise ValueError("Les courses intermédiaires doivent être entre la date de début et la date de course principale")

    def calculate_ef_pace(self) -> timedelta:
        """
        Calcule l'allure d'endurance fondamentale selon les règles:
        - Pour course de type standard: marathon + 30s
        - Pour course de type 'autre': règles spécifiques selon l'allure calculée
        """
        if self.main_race.race_type != RaceType.OTHER:
            # Règle standard: marathon + 30s
            return self.pace_marathon + timedelta(seconds=30)

        # Règles spécifiques pour le type 'autre'
        if self.main_race.target_pace is None:
            raise ValueError("L'allure cible doit être définie pour les courses de type 'autre'")

        calculated_pace = self.main_race.target_pace

        # Appliquer les règles spécifiques
        if calculated_pace < self.pace_10k:
            # Plus rapide que l'allure 10K: +40s
            return calculated_pace + timedelta(seconds=40)
        elif calculated_pace < self.pace_marathon:
            # Entre l'allure 10K et marathon: +30s
            return calculated_pace + timedelta(seconds=30)
        else:
            # Plus lente que l'allure marathon: +20s
            return calculated_pace + timedelta(seconds=20)

    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'objet en dictionnaire pour sérialisation JSON"""
        return {
            "start_date": self.start_date.isoformat(),
            "main_race": self.main_race.to_dict(),
            "pace_5k": self.pace_5k.total_seconds(),
            "pace_10k": self.pace_10k.total_seconds(),
            "pace_half_marathon": self.pace_half_marathon.total_seconds(),
            "pace_marathon": self.pace_marathon.total_seconds(),
            "sessions_per_week": self.sessions_per_week,
            "min_volume": self.min_volume,
            "max_volume": self.max_volume,
            "intermediate_races": [race.to_dict() for race in self.intermediate_races]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserData':
        """Crée un objet UserData à partir d'un dictionnaire"""
        # Conversion des types
        start_date = date.fromisoformat(data["start_date"])
        main_race = Course.from_dict(data["main_race"])
        pace_5k = timedelta(seconds=data["pace_5k"])
        pace_10k = timedelta(seconds=data["pace_10k"])
        pace_half_marathon = timedelta(seconds=data["pace_half_marathon"])
        pace_marathon = timedelta(seconds=data["pace_marathon"])
        intermediate_races = [Course.from_dict(race) for race in data.get("intermediate_races", [])]

        return cls(
            start_date=start_date,
            main_race=main_race,
            pace_5k=pace_5k,
            pace_10k=pace_10k,
            pace_half_marathon=pace_half_marathon,
            pace_marathon=pace_marathon,
            sessions_per_week=data["sessions_per_week"],
            min_volume=data["min_volume"],
            max_volume=data["max_volume"],
            intermediate_races=intermediate_races
        )

    @property
    def total_weeks(self) -> int:
        """Calcule le nombre total de semaines du plan"""
        return (self.main_race.race_date - self.start_date).days // 7 + 1  # +1 pour inclure la semaine de la course

    @property
    def specific_pace(self) -> timedelta:
        """
        Retourne l'allure spécifique de la course principale selon son type
        """
        if self.main_race.race_type == RaceType.TEN_K:
            return self.pace_10k
        elif self.main_race.race_type == RaceType.HALF_MARATHON:
            return self.pace_half_marathon
        elif self.main_race.race_type == RaceType.MARATHON:
            return self.pace_marathon
        else:
            # Pour le type 'autre', utiliser l'allure calculée
            if self.main_race.target_pace is None:
                raise ValueError("L'allure cible doit être définie pour les courses de type 'autre'")
            return self.main_race.target_pace