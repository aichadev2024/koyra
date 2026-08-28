@echo off
cd /d C:\DEV\koyra
call venv\Scripts\activate.bat
python manage.py makemigrations catalogue
python manage.py migrate
python manage.py createsuperuser --noinput --username admin --email admin@koyradistribution.com
echo FINISHED
