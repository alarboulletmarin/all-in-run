# All-in-Run

Application de génération de plans d'entraînement personnalisés pour les courses de fond (10K, semi-marathon, marathon et autres distances).

## Caractéristiques

- Génération de plans d'entraînement adaptés à votre objectif
- Prise en compte de votre niveau actuel (allures)
- Intégration de courses intermédiaires
- Visualisation interactive du plan
- Exportation vers différents formats (ICS, PDF, CSV)
- Simulation de plans alternatifs
- Support multilingue (Français, Anglais, Espagnol)

## Installation

### Avec Poetry (recommandé)

```bash
# Cloner le dépôt
git clone https://github.com/yourusername/all-in-run.git
cd all-in-run

# Installer avec Poetry
poetry install

# Lancer l'application
poetry run streamlit run app.py
```

### Avec pip

```bash
# Cloner le dépôt
git clone https://github.com/yourusername/all-in-run.git
cd all-in-run

# Installer avec pip
pip install -e .

# Lancer l'application
streamlit run app.py
```

## Utilisation

1. Renseignez vos informations personnelles (allures actuelles, volume d'entraînement)
2. Définissez votre objectif (type de course, date)
3. Ajoutez d'éventuelles courses intermédiaires
4. Générez votre plan d'entraînement
5. Consultez et exportez votre plan
6. Simulez des plans alternatifs si nécessaire

## Architecture

L'application suit une architecture en couches pour une meilleure modularité et maintenabilité :

- **Modèles** : Structures de données (plan, séances, utilisateur)
- **Services** : Logique métier (génération de plan, calcul de phases)
- **Contrôleurs** : Orchestration des opérations
- **Interface utilisateur** : Composants Streamlit

## Développement

### Structure du projet

```
all_in_run/
│
├── config/                     # Configuration
├── models/                     # Modèles de données
├── controllers/                # Contrôleurs
├── services/                   # Services métier
├── ui/                         # Interface utilisateur
│   ├── components/             # Composants réutilisables
│   └── pages/                  # Pages de l'application
├── utils/                      # Utilitaires
└── i18n/                       # Internationalisation
```

### Ajout d'une nouvelle fonctionnalité

1. Définissez les modèles nécessaires
2. Implémentez la logique métier dans les services
3. Créez ou modifiez les contrôleurs pour orchestrer les opérations
4. Développez l'interface utilisateur
5. Ajoutez les traductions nécessaires

## Licence

MIT