#!/bin/bash --login

# Activate anaconda environment for the application
conda activate $APP_ENV

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."
    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done
    echo "PostgreSQL started"
fi

if [ "$RUN_MIGRATION" ]
then
    echo "Running inital migrations"
    python manage.py makemigrations --noinput
    python manage.py migrate --noinput
    python manage.py collectstatic --noinput
    python manage.py initsuperuser
    echo "Migration run completed"
fi

exec "$@"
