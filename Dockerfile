# Image de base légère avec Python
FROM python:3.9-slim as builder

# Définir des variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Créer un utilisateur non-root
RUN groupadd -r app && useradd -r -g app app

# Créer et définir le répertoire de travail
WORKDIR /app

# Copier uniquement les fichiers de dépendances d'abord pour optimiser le cache Docker
COPY requirements.txt .

# Installer les dépendances
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Image finale plus légère
FROM python:3.9-slim

# Maintainer label pour information
LABEL maintainer="All-in-Run <contact@example.com>"

# Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_HOME=/app

# Créer le même utilisateur non-root
RUN groupadd -r app && useradd -r -g app app

# Définir le répertoire de travail
WORKDIR $APP_HOME

# Copier les dépendances depuis le builder
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages

# Créer le répertoire pour stocker les données
RUN mkdir -p $APP_HOME/data && chown -R app:app $APP_HOME

# Copier le code source de l'application
COPY --chown=app:app . $APP_HOME/

# Exposition du port Streamlit
EXPOSE 8501

# Changer d'utilisateur pour des raisons de sécurité
USER app

# Définir le volume pour la persistance des données
VOLUME $APP_HOME/data

# Healthcheck pour s'assurer que l'application est en cours d'exécution
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/ || exit 1

# Définir l'entrypoint et la commande par défaut
ENTRYPOINT ["streamlit"]
CMD ["run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
