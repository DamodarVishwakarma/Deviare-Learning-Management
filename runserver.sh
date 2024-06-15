#!/bin/bash

celery -A deviare worker -l INFO --logfile celery.log &
# Initialize celery beat
celery -A deviare beat -S django -l INFO --logfile beat.log &
./manage.py runserver 0.0.0.0:8000