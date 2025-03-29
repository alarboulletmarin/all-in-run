"""
Gestion du stockage local pour l'application.
"""
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, List, Union

import streamlit as st


class StorageManager:
    """Gestionnaire de stockage local pour l'application"""

    def __init__(self, use_session_state: bool = True):
        """
        Initialise le gestionnaire de stockage

        Args:
            use_session_state: Si True, utilise st.session_state comme stockage,
                              sinon utilise des fichiers locaux
        """
        self.use_session_state = use_session_state
        self.storage_dir = os.path.join(os.path.expanduser("~"), ".all_in_run")

        # Créer le répertoire de stockage s'il n'existe pas
        if not self.use_session_state and not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)

    def save_plan(self, plan) -> None:
        """
        Sauvegarde un plan d'entraînement

        Args:
            plan: Plan d'entraînement à sauvegarder
        """
        # Import moved here to avoid circular import
        from models.plan import TrainingPlan

        if self.use_session_state:
            # Utiliser st.session_state pour stocker le plan
            st.session_state["current_plan"] = plan
        else:
            # Utiliser un fichier local pour stocker le plan
            plan_data = plan.to_dict()
            filename = f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = os.path.join(self.storage_dir, filename)

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(plan_data, f, indent=2)

            # Sauvegarder également la référence au plan courant
            current_plan_ref = {"filename": filename}
            current_plan_path = os.path.join(
                self.storage_dir, "current_plan.json")

            with open(current_plan_path, 'w', encoding='utf-8') as f:
                json.dump(current_plan_ref, f, indent=2)

    def load_plan(self) -> Optional['TrainingPlan']:
        """
        Charge le plan d'entraînement courant

        Returns:
            Plan d'entraînement ou None si aucun plan n'est stocké
        """
        # Import moved here to avoid circular import
        from models.plan import TrainingPlan

        if self.use_session_state:
            # Récupérer le plan depuis st.session_state
            return st.session_state.get("current_plan")
        else:
            # Récupérer le plan depuis un fichier local
            current_plan_path = os.path.join(
                self.storage_dir, "current_plan.json")

            if not os.path.exists(current_plan_path):
                return None

            try:
                with open(current_plan_path, 'r', encoding='utf-8') as f:
                    current_plan_ref = json.load(f)

                filename = current_plan_ref.get("filename")
                if not filename:
                    return None

                filepath = os.path.join(self.storage_dir, filename)

                if not os.path.exists(filepath):
                    return None

                with open(filepath, 'r', encoding='utf-8') as f:
                    plan_data = json.load(f)

                return TrainingPlan.from_dict(plan_data)

            except (json.JSONDecodeError, IOError) as e:
                print(f"Erreur lors du chargement du plan: {e}")
                return None

    def save_user_preferences(self, preferences: Dict[str, Any]) -> None:
        """
        Sauvegarde les préférences utilisateur

        Args:
            preferences: Dictionnaire des préférences
        """
        if self.use_session_state:
            # Utiliser st.session_state pour stocker les préférences
            st.session_state["user_preferences"] = preferences
        else:
            # Utiliser un fichier local pour stocker les préférences
            preferences_path = os.path.join(
                self.storage_dir, "preferences.json")

            with open(preferences_path, 'w', encoding='utf-8') as f:
                json.dump(preferences, f, indent=2)

    def load_user_preferences(self) -> Dict[str, Any]:
        """
        Charge les préférences utilisateur

        Returns:
            Dictionnaire des préférences ou dictionnaire vide si aucune préférence n'est stockée
        """
        if self.use_session_state:
            # Récupérer les préférences depuis st.session_state
            return st.session_state.get("user_preferences", {})
        else:
            # Récupérer les préférences depuis un fichier local
            preferences_path = os.path.join(
                self.storage_dir, "preferences.json")

            if not os.path.exists(preferences_path):
                return {}

            try:
                with open(preferences_path, 'r', encoding='utf-8') as f:
                    preferences = json.load(f)

                return preferences

            except (json.JSONDecodeError, IOError) as e:
                print(f"Erreur lors du chargement des préférences: {e}")
                return {}

    def save_user_input(self, user_input: Dict[str, Any]) -> None:
        """
        Sauvegarde les entrées utilisateur

        Args:
            user_input: Dictionnaire des entrées utilisateur
        """
        if self.use_session_state:
            # Utiliser st.session_state pour stocker les entrées
            st.session_state["user_input"] = user_input
        else:
            # Utiliser un fichier local pour stocker les entrées
            input_path = os.path.join(self.storage_dir, "user_input.json")

            # Convertir les types non-JSON en chaînes
            serializable_input = {}
            for key, value in user_input.items():
                if hasattr(value, "isoformat"):  # Pour les dates
                    serializable_input[key] = value.isoformat()
                elif hasattr(value, "total_seconds"):  # Pour les timedelta
                    serializable_input[key] = value.total_seconds()
                else:
                    serializable_input[key] = value

            with open(input_path, 'w', encoding='utf-8') as f:
                json.dump(serializable_input, f, indent=2)

    def load_user_input(self) -> Dict[str, Any]:
        """
        Charge les entrées utilisateur

        Returns:
            Dictionnaire des entrées utilisateur ou dictionnaire vide si aucune entrée n'est stockée
        """
        if self.use_session_state:
            # Récupérer les entrées depuis st.session_state
            return st.session_state.get("user_input", {})
        else:
            # Récupérer les entrées depuis un fichier local
            input_path = os.path.join(self.storage_dir, "user_input.json")

            if not os.path.exists(input_path):
                return {}

            try:
                with open(input_path, 'r', encoding='utf-8') as f:
                    user_input = json.load(f)

                return user_input

            except (json.JSONDecodeError, IOError) as e:
                print(
                    f"Erreur lors du chargement des entrées utilisateur: {e}")
                return {}

    def list_saved_plans(self) -> List[Dict[str, Any]]:
        """
        Liste tous les plans sauvegardés

        Returns:
            Liste des plans sauvegardés avec métadonnées
        """
        if self.use_session_state:
            # Avec st.session_state, on ne peut stocker qu'un seul plan
            plan = st.session_state.get("current_plan")
            if plan:
                return [{
                    "name": "Plan courant",
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "plan": plan
                }]
            return []
        else:
            # Lister tous les fichiers de plan dans le répertoire de stockage
            plans = []

            if not os.path.exists(self.storage_dir):
                return []

            for filename in os.listdir(self.storage_dir):
                if filename.startswith("plan_") and filename.endswith(".json"):
                    filepath = os.path.join(self.storage_dir, filename)

                    try:
                        # Extraire la date de création du nom de fichier
                        # Enlever "plan_" et ".json"
                        created_at_str = filename[5:-5]
                        created_at = datetime.strptime(
                            created_at_str, "%Y%m%d_%H%M%S")

                        # Charger juste les métadonnées du plan
                        with open(filepath, 'r', encoding='utf-8') as f:
                            plan_data = json.load(f)

                        # Extraire les informations importantes
                        user_data = plan_data.get("user_data", {})

                        plans.append({
                            "filename": filename,
                            "created_at": created_at.strftime("%Y-%m-%d %H:%M:%S"),
                            "race_type": user_data.get("main_race", {}).get("race_type", ""),
                            "race_date": user_data.get("main_race", {}).get("race_date", ""),
                            "start_date": user_data.get("start_date", "")
                        })

                    except (json.JSONDecodeError, IOError, ValueError) as e:
                        print(
                            f"Erreur lors du chargement du plan {filename}: {e}")

            # Trier par date de création (plus récent en premier)
            return sorted(plans, key=lambda p: p["created_at"], reverse=True)

    def load_plan_by_filename(self, filename: str) -> Optional['TrainingPlan']:
        """
        Charge un plan d'entraînement à partir de son nom de fichier

        Args:
            filename: Nom du fichier contenant le plan

        Returns:
            Plan d'entraînement ou None si le fichier n'existe pas
        """
        # Import moved here to avoid circular import
        from models.plan import TrainingPlan

        if self.use_session_state:
            # Avec st.session_state, on ne peut charger que le plan courant
            return st.session_state.get("current_plan")
        else:
            filepath = os.path.join(self.storage_dir, filename)

            if not os.path.exists(filepath):
                return None

            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    plan_data = json.load(f)

                return TrainingPlan.from_dict(plan_data)

            except (json.JSONDecodeError, IOError) as e:
                print(f"Erreur lors du chargement du plan {filename}: {e}")
                return None

    def delete_plan(self, filename: str) -> bool:
        """
        Supprime un plan d'entraînement

        Args:
            filename: Nom du fichier contenant le plan

        Returns:
            True si la suppression a réussi, False sinon
        """
        if self.use_session_state:
            # Avec st.session_state, on ne peut supprimer que le plan courant
            if "current_plan" in st.session_state:
                del st.session_state["current_plan"]
                return True
            return False
        else:
            filepath = os.path.join(self.storage_dir, filename)

            if not os.path.exists(filepath):
                return False

            try:
                os.remove(filepath)

                # Si c'est le plan courant, supprimer également la référence
                current_plan_path = os.path.join(
                    self.storage_dir, "current_plan.json")

                if os.path.exists(current_plan_path):
                    try:
                        with open(current_plan_path, 'r', encoding='utf-8') as f:
                            current_plan_ref = json.load(f)

                        if current_plan_ref.get("filename") == filename:
                            os.remove(current_plan_path)

                    except (json.JSONDecodeError, IOError) as e:
                        print(
                            f"Erreur lors de la vérification du plan courant: {e}")

                return True

            except IOError as e:
                print(f"Erreur lors de la suppression du plan {filename}: {e}")
                return False


# Créer une instance de StorageManager par défaut
storage_manager = StorageManager()
