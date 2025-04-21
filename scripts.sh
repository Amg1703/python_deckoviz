#!/bin/bash

# Run makemigrations only if there are changes
if python3 manage.py makemigrations --check --dry-run | grep -q "No changes detected"; then
    echo "No changes detected in models."
else
    python3 manage.py makemigrations
fi



# Always run migrate (safe to run multiple times)
python3 manage.py migrate



#collect static files
# python manage.py collectstatic

 
# Run the development server (you can customize this for production)
python3 manage.py runserver 0.0.0.0:8000


# Run the ASGI server using Uvicorn
# uvicorn careti.asgi:application --host 0.0.0.0 --port 8000 --reload
# daphne  -p 8000 careti.asgi:application
# gunicorn -w 4 -b 0.0.0.0:8000 main:app

 