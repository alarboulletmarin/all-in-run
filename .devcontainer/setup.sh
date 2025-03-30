#!/bin/bash
set -e

echo "🚀 Configuration de l'environnement de développement..."

# Ajout du chemin local au PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Installation des outils de développement
echo "📦 Installation des outils de développement..."
pip install --no-cache-dir pre-commit &> /dev/null

# Configuration de pre-commit
echo "🔧 Configuration de pre-commit..."
pre-commit install &> /dev/null

# Installation des dépendances du projet avec Poetry
echo "📚 Installation des dépendances avec Poetry..."
poetry config virtualenvs.in-project true
poetry install --no-interaction --no-root --with dev

# Installation du package en mode éditable
echo "🔗 Installation du package en mode éditable..."
pip install -e . &> /dev/null

echo "✅ Environnement de développement prêt !"
