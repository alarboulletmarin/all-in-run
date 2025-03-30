# Notice d'installation - All-in-Run

Ce document détaille les différentes méthodes pour installer l'application All-in-Run.

## Sommaire
- [Prérequis](#prérequis)
- [Installation avec Docker (recommandée)](#installation-avec-docker-recommandée)
- [Installation locale avec Poetry](#installation-locale-avec-poetry)
- [Installation manuelle avec pip](#installation-manuelle-avec-pip)
- [Vérification de l'installation](#vérification-de-linstallation)

## Prérequis

### Pour l'installation avec Docker
- Docker installé sur votre système
- Git (optionnel, pour cloner le dépôt)

### Pour l'installation locale
- Python 3.12 ou supérieur
- Poetry (pour la gestion des dépendances) ou pip
- Git (optionnel, pour cloner le dépôt)

## Installation avec Docker (recommandée)

L'installation avec Docker est la méthode la plus simple et la plus fiable pour déployer All-in-Run.

```bash
# 1. Téléchargez le dépôt (si vous ne l'avez pas déjà)
git clone https://github.com/alarboulletmarin/all-in-run.git
cd all-in-run

# 2. Construisez l'image Docker
docker build -t all-in-run .
```

## Installation locale avec Poetry

Poetry est l'outil de gestion de dépendances recommandé pour Python.

```bash
# 1. Téléchargez le dépôt (si vous ne l'avez pas déjà)
git clone https://github.com/alarboulletmarin/all-in-run.git
cd all-in-run

# 2. Installez les dépendances avec Poetry
poetry install

# 3. (Optionnel) Installez les dépendances de développement
poetry install --with dev
```

## Installation manuelle avec pip

Si vous n'utilisez pas Poetry, vous pouvez installer les dépendances avec pip.

```bash
# 1. Téléchargez le dépôt (si vous ne l'avez pas déjà)
git clone https://github.com/alarboulletmarin/all-in-run.git
cd all-in-run

# 2. Créez et activez un environnement virtuel (recommandé)
python -m venv venv
source venv/bin/activate  # Sur Windows : venv\Scripts\activate

# 3. Installez les dépendances
pip install -r requirements.txt
```

## Vérification de l'installation

Pour vérifier que l'installation s'est bien déroulée, vous pouvez lancer l'application en mode test :

### Avec Docker
```bash
# Lancer un conteneur pour tester
docker run -p 8501:8501 all-in-run
```

### Avec Poetry
```bash
# Lancer l'application
poetry run streamlit run app.py
```

### Avec pip et environnement virtuel
```bash
# Assurez-vous que l'environnement virtuel est activé
streamlit run app.py
```

Ouvrez votre navigateur et accédez à http://localhost:8501. Vous devriez voir l'interface utilisateur d'All-in-Run.
