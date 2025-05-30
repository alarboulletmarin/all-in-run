# 🏃 All-in-Run

![Python](https://img.shields.io/badge/Python-3.12-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Docker](https://img.shields.io/badge/Docker-ready-blue.svg)

**All-in-Run** est une application web de génération de plans d'entraînement personnalisés pour coureurs. Elle permet de créer un plan adapté à vos objectifs, de visualiser votre progression et d'exporter votre planning vers différentes plateformes.

![All-in-Run Demo](/images/demo.gif)

## ✨ Fonctionnalités

- 📊 **Génération de plans d'entraînement** adaptés à votre niveau et objectifs
- 📅 **Visualisation du calendrier** d'entraînement avec détail des séances
- 📈 **Statistiques et analyses** de la progression et charge d'entraînement
- 📱 **Exportation multi-plateforme** (calendriers, montres connectées, PDF)
- 🌍 **Multi-langue** (Français, Anglais)
- 🔄 **Ajustement dynamique** du plan selon vos performances

## 🚀 Démarrage rapide

### Option 1: Avec Docker (recommandé)

La méthode la plus simple pour démarrer All-in-Run est d'utiliser Docker:

```bash
# Télécharger le dépôt
git clone https://github.com/alarboulletmarin/all-in-run.git
cd all-in-run

# Lancer avec Docker
docker build -t all-in-run .
docker run -p 8501:8501 all-in-run
```

Accédez ensuite à l'application dans votre navigateur: http://localhost:8501

### Option 2: Installation locale

#### Prérequis

- Python 3.12+
- Poetry (gestionnaire de dépendances)

#### Installation

```bash
# Télécharger le dépôt
git clone https://github.com/alarboulletmarin/all-in-run.git
cd all-in-run

# Installer les dépendances avec Poetry
poetry install

# Lancer l'application
poetry run streamlit run app.py
```

## 📖 Guide d'utilisation

### Création d'un plan d'entraînement

1. Sur la page d'accueil, saisissez vos informations personnelles (qui ne sont PAS stockées):
   - Objectif de course
   - Niveau actuel
   - Disponibilité hebdomadaire
   - Date de l'objectif

2. Cliquez sur "Générer mon plan"

3. Explorez votre plan personnalisé dans les différents onglets:
   - Vue d'ensemble
   - Calendrier
   - Détails des séances
   - Statistiques

### Exportation du plan

L'application offre plusieurs options d'exportation:

- **Calendrier (ICS)**: Importez votre plan dans Google Calendar, Apple Calendar, etc.
- **PDF**: Document imprimable avec tous les détails de votre programme
- **Montres connectées**: Formats compatibles avec Garmin, Apple Watch, etc.
- **Données brutes**: Export JSON pour sauvegarde ou analyse externe

## 🧩 Structure du projet

```
all-in-run/
├── app.py                # Point d'entrée de l'application
├── config/              # Configuration et paramètres
├── controllers/         # Contrôleurs (logique métier)
├── data/                # Données générées et stockées
├── i18n/                # Fichiers de traduction
├── models/              # Modèles de données
├── services/            # Services métier
├── ui/                  # Interface utilisateur
│   ├── components/      # Composants UI réutilisables
│   ├── pages/           # Pages de l'application
│   └── utils/           # Utilitaires pour l'UI
├── utils/               # Utilitaires généraux
├── Dockerfile           # Configuration Docker
└── docker-compose.yml   # Configuration docker-compose
```

## 🐳 Déploiement avec Docker

### Personnalisation du déploiement

Vous pouvez personnaliser le déploiement en modifiant le fichier `docker-compose.yml`:

```yaml
version: '3.8'

services:
  all-in-run:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: all-in-run
    ports:
      - "8501:8501"  # Modifiez le port si nécessaire
    volumes:
      - ./data:/app/data  # Persistance des données
    restart: unless-stopped
    environment:
      - STREAMLIT_SERVER_MAX_UPLOAD_SIZE=10
      - STREAMLIT_THEME_PRIMARY_COLOR=#FF4B4B
```

### Options de configuration Docker

- **Ports**: Modifiez `"8501:8501"` pour changer le port d'accès
- **Volumes**: Personnalisez le stockage persistant avec `./data:/app/data`
- **Variables d'environnement**: Configurez Streamlit avec des variables comme `STREAMLIT_THEME_PRIMARY_COLOR`

## 🧪 Développement avec DevContainer

### Qu'est-ce qu'un DevContainer ?

Un DevContainer (conteneur de développement) est un environnement de développement préconfiguré qui s'exécute dans un conteneur Docker. Cette approche permet de :

- Standardiser l'environnement de développement entre tous les contributeurs
- Éviter les problèmes de "ça marche sur ma machine"
- Intégrer facilement les nouveaux développeurs au projet
- Isoler les dépendances du projet de votre système

### Pourquoi utiliser un DevContainer pour All-in-Run ?

- Garantit que tous les développeurs utilisent la même version de Python et des bibliothèques
- Inclut tous les outils nécessaires préinstallés (linters, formatters, etc.)
- Offre un environnement de test identique à la production
- Simplifie la collaboration et le débogage

### Comment utiliser le DevContainer

#### Prérequis

- [Visual Studio Code](https://code.visualstudio.com/)
- [Extension Remote - Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
- [Docker](https://www.docker.com/products/docker-desktop/)

#### Démarrage

1. Clonez le dépôt All-in-Run
   ```bash
   git clone https://github.com/votre-org/all-in-run.git
   cd all-in-run
   ```

2. Ouvrez le projet dans VS Code
   ```bash
   code .
   ```

3. Lorsque VS Code détecte le fichier `.devcontainer`, il proposera de "Reopen in Container". Cliquez sur cette option.
   - Alternativement : Ouvrez la palette de commandes (F1 ou Ctrl+Shift+P) et choisissez "Remote-Containers: Reopen in Container"

4. VS Code construira et démarrera le conteneur de développement, puis ouvrira le projet dans ce conteneur. La première construction peut prendre quelques minutes.

5. Une fois dans le conteneur, vous disposez d'un environnement complet avec :
   - Python 3.9 préinstallé
   - Toutes les dépendances du projet installées
   - Configuration des linters et formatters
   - Accès au terminal intégré dans le conteneur

#### Personnalisation

Si vous souhaitez personnaliser l'environnement de développement, vous pouvez modifier les fichiers dans le dossier `.devcontainer` :

- `devcontainer.json` : Configuration de l'environnement VS Code
- `Dockerfile` : Définition de l'image de conteneur

## 🛠️ Développement

### Environnement de développement

```bash
# Installer les dépendances de développement
poetry install --with dev

# Lancer les tests
poetry run pytest

# Vérifier le style du code
poetry run black .
poetry run isort .
poetry run flake8
```

### Architecture du projet

All-in-Run utilise une architecture MVC (Modèle-Vue-Contrôleur):

- **Modèles**: Définition des structures de données (plans, sessions, utilisateurs)
- **Vues**: Interface utilisateur Streamlit
- **Contrôleurs**: Logique de traitement et génération des plans

## 📄 Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 🙏 Remerciements

- [Streamlit](https://streamlit.io/) - Framework pour applications de données
- [Plotly](https://plotly.com/) - Visualisations interactives
- [ReportLab](https://www.reportlab.com/) - Génération de PDF
- [ICS](https://github.com/ics-py/ics-py) - Manipulation de fichiers iCalendar

---

Développé avec ❤️ et passion !