#!/usr/bin/env bash
echo '>>> STARTING SSH SERVER...'
/usr/sbin/sshd -D 2>&1 &
echo '>>> STARTING REDIS SERVER...'
redis-server --daemonize yes

mig=$1

/usr/local/bin/confd -onetime -backend env

cd /backend/project/


if [[ $mig == 'true' ]]
then
  cd /backend/
  python3.7 manage.py migrate
  exit 0
fi


#chown -R www-data:www-data /etc/apache2/FormFiller/
cd /backend/  
# Celery in detached mode
celery -A deviare worker -l INFO --logfile celery.log &

# Initialize celery beat 
celery -A deviare beat -S django -l INFO --logfile beat.log &

# Run Django webserver 
python3.7 manage.py runserver 0.0.0.0:8080

