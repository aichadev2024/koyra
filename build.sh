#!/usr/bin/env bash
# Script de build exécuté par Render à chaque déploiement.
# NB : les migrations tournent au démarrage (startCommand), pas ici :
# la base n'est pas joignable pendant la phase de build sur Render.
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
