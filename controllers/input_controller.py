"""
Contrôleur pour la validation et le traitement des entrées utilisateur.
"""
from datetime import date, timedelta
from typing import Dict, Any, Tuple, List, Optional

from models.user_data import UserData
from models.course import Course, RaceType
from utils.validators import (
    validate_date_range,
    validate_course_info,
    validate_paces,
    validate_volume,
    validate_sessions_per_week,
    validate_intermediate_races,
    validate_user_input
)
from utils.time_converter import parse_time_string, parse_pace_string
from utils.storage import storage_manager


class InputController:
    """Contrôleur pour la validation et le traitement des entrées utilisateur"""

    def validate_input(self, user_input: Dict[str, Any], lang: str = "fr") -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Valide les entrées utilisateur

        Args:
            user_input: Dictionnaire des entrées à valider
            lang: Code de langue pour les messages d'erreur

        Returns:
            Tuple (valide, message d'erreur, entrées validées)
        """
        valid, message, validated_input = validate_user_input(user_input, lang)
        return valid, message, validated_input if valid else None

    def create_user_data(self, validated_input: Dict[str, Any]) -> UserData:
        """
        Crée un objet UserData à partir des entrées validées

        Args:
            validated_input: Dictionnaire des entrées validées

        Returns:
            Objet UserData
        """
        # Créer la course principale
        race_type_str = validated_input.get("race_type")
        race_type = RaceType(race_type_str) if isinstance(race_type_str, str) else race_type_str

        main_race = Course(
            race_date=validated_input["race_date"],
            race_type=race_type,
            distance=validated_input.get("distance"),
            target_time=validated_input.get("target_time"),
            is_main_race=True
        )

        # Créer les courses intermédiaires
        intermediate_races = []
        for race_data in validated_input.get("intermediate_races", []):
            race = Course(
                race_date=race_data["race_date"],
                race_type=RaceType(race_data["race_type"]) if isinstance(race_data["race_type"], str) else race_data["race_type"],
                distance=race_data.get("distance"),
                target_pace=race_data.get("target_pace"),
                is_main_race=False
            )
            intermediate_races.append(race)

        # Créer l'objet UserData
        user_data = UserData(
            start_date=validated_input["start_date"],
            main_race=main_race,
            pace_5k=validated_input["pace_5k"],
            pace_10k=validated_input["pace_10k"],
            pace_half_marathon=validated_input["pace_half_marathon"],
            pace_marathon=validated_input["pace_marathon"],
            sessions_per_week=validated_input["sessions_per_week"],
            min_volume=validated_input["min_volume"],
            max_volume=validated_input["max_volume"],
            intermediate_races=intermediate_races
        )

        return user_data

    def save_input(self, user_input: Dict[str, Any]) -> None:
        """
        Sauvegarde les entrées utilisateur

        Args:
            user_input: Dictionnaire des entrées à sauvegarder
        """
        storage_manager.save_user_input(user_input)

    def load_input(self) -> Dict[str, Any]:
        """
        Charge les entrées utilisateur sauvegardées

        Returns:
            Dictionnaire des entrées chargées ou dictionnaire vide si aucune entrée n'est sauvegardée
        """
        return storage_manager.load_user_input()

    def process_form_data(self, form_data: Dict[str, Any], lang: str = "fr") -> Tuple[bool, str, Optional[UserData]]:
        """
        Traite les données de formulaire pour les convertir en entrées validées puis en UserData

        Args:
            form_data: Données brutes du formulaire
            lang: Code de langue pour les messages d'erreur

        Returns:
            Tuple (succès, message, UserData)
        """
        # Prétraiter les données du formulaire
        processed_input = self._preprocess_form_data(form_data)

        # Valider les entrées
        valid, message, validated_input = self.validate_input(processed_input, lang)
        if not valid:
            return False, message, None

        # Créer l'objet UserData
        try:
            user_data = self.create_user_data(validated_input)
            return True, "", user_data
        except Exception as e:
            return False, f"Erreur lors de la création des données utilisateur: {str(e)}", None

    def _preprocess_form_data(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prétraite les données du formulaire

        Args:
            form_data: Données brutes du formulaire

        Returns:
            Données prétraitées
        """
        preprocessed = {}

        # Copier les champs simples
        for key in ["start_date", "race_date", "race_type", "sessions_per_week",
                    "min_volume", "max_volume"]:
            if key in form_data:
                preprocessed[key] = form_data[key]

        # Traiter les champs spéciaux
        if "distance" in form_data and form_data.get("race_type") == "autre":
            preprocessed["distance"] = float(form_data["distance"])

        # Traiter le temps cible
        if "target_time" in form_data and form_data.get("race_type") == "autre":
            target_time = parse_time_string(form_data["target_time"])
            if target_time:
                preprocessed["target_time"] = target_time

        # Traiter les allures
        for pace_key in ["pace_5k", "pace_10k", "pace_half_marathon", "pace_marathon"]:
            if pace_key in form_data:
                pace = parse_pace_string(form_data[pace_key])
                if pace:
                    preprocessed[pace_key] = pace

        # Traiter les courses intermédiaires
        if "intermediate_races" in form_data:
            preprocessed["intermediate_races"] = []

            for race_data in form_data["intermediate_races"]:
                processed_race = {}

                # Copier les champs simples
                for key in ["race_date", "race_type"]:
                    if key in race_data:
                        processed_race[key] = race_data[key]

                # Traiter les champs spéciaux
                if "distance" in race_data and race_data.get("race_type") == "autre":
                    processed_race["distance"] = float(race_data["distance"])

                # Traiter l'allure visée
                if "target_pace" in race_data:
                    target_pace = parse_pace_string(race_data["target_pace"])
                    if target_pace:
                        processed_race["target_pace"] = target_pace

                preprocessed["intermediate_races"].append(processed_race)

        return preprocessed