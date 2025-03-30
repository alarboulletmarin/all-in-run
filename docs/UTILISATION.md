# Notice d'utilisation - All-in-Run

Ce document explique comment exécuter et utiliser l'application All-in-Run.

## Sommaire
- [Lancement de l'application](#lancement-de-lapplication)
- [Interface utilisateur](#interface-utilisateur)
- [Création d'un plan d'entraînement](#création-dun-plan-dentraînement)
- [Exportation du plan](#exportation-du-plan)
- [Options de configuration](#options-de-configuration)
- [Dépannage](#dépannage)

## Lancement de l'application

### Avec Docker
```bash
# Lancer le conteneur
docker run -p 8501:8501 all-in-run
```

### Avec Poetry
```bash
# À partir du répertoire du projet
poetry run streamlit run app.py
```

### Avec pip (dans un environnement virtuel)
```bash
# Activer l'environnement virtuel
source venv/bin/activate  # Sur Windows : venv\Scripts\activate

# Lancer l'application
streamlit run app.py
```

Dans tous les cas, ouvrez votre navigateur à l'adresse **http://localhost:8501** pour accéder à l'interface.

## Interface utilisateur

L'interface d'All-in-Run est divisée en plusieurs sections accessibles depuis la barre latérale :

- **Accueil / Création de plan** : Saisie des informations pour générer un nouveau plan
- **Visualisation du plan** : Affichage détaillé du plan d'entraînement généré
- **Statistiques** : Analyses et graphiques relatifs au plan
- **Exportation** : Options pour exporter le plan vers différents formats
- **Simulation** : Outil de simulation pour optimiser votre plan

## Création d'un plan d'entraînement

1. Depuis la page d'accueil, renseignez les informations demandées :
   - Objectif de course (type et date)
   - Niveau actuel (temps ou allure sur différentes distances)
   - Disponibilité hebdomadaire (nombre de séances par semaine)
   - Date de début d'entraînement

2. Cliquez sur "Générer mon plan" pour créer votre plan personnalisé

3. Naviguez entre les différents onglets pour explorer votre plan :
   - Vue d'ensemble
   - Calendrier
   - Détails des séances
   - Statistiques

## Exportation du plan

All-in-Run permet d'exporter votre plan dans plusieurs formats :

### Exportation au format calendrier (ICS)

1. Allez dans la section "Exportation"
2. Sélectionnez "Calendrier (ICS)"
3. Configurez les options :
   - Nom du calendrier
   - Inclusion des jours de repos
   - Rappels
   - Heure de début par défaut
4. Cliquez sur "Exporter vers calendrier"
5. Téléchargez le fichier ICS et importez-le dans votre application de calendrier préférée

### Exportation au format PDF

1. Allez dans la section "Exportation"
2. Sélectionnez "PDF"
3. Configurez les options :
   - Taille de papier (A4, Letter, Legal)
   - Orientation (portrait/paysage)
   - Inclusion des détails et statistiques
4. Cliquez sur "Générer PDF"
5. Téléchargez le document PDF généré

### Exportation pour montres connectées

1. Allez dans la section "Exportation"
2. Sélectionnez votre type d'appareil (Garmin, Apple Watch)
3. Suivez les instructions spécifiques à votre appareil
4. Téléchargez le fichier au format approprié (TCX pour Garmin, ICS pour Apple Watch)

## Options de configuration

Certains aspects de l'application peuvent être configurés :

- **Langue** : Sélectionnez votre langue préférée dans la barre latérale (Français, Anglais)
- **Unités** : Choisissez entre métrique (km) et impérial (miles) dans les paramètres
- **Thème** : L'application s'adapte au thème de Streamlit (clair/sombre)

## Dépannage

### Problèmes courants

1. **L'application ne démarre pas**
   - Vérifiez que le port 8501 n'est pas déjà utilisé
   - Assurez-vous que toutes les dépendances sont correctement installées

2. **Erreur lors de la génération du plan**
   - Vérifiez que les données saisies sont cohérentes
   - Assurez-vous que la date de l'objectif est suffisamment éloignée de la date de début

3. **Problèmes d'exportation**
   - Pour les PDF : vérifiez que ReportLab est correctement installé
   - Pour les fichiers ICS : assurez-vous que le module ics est disponible

