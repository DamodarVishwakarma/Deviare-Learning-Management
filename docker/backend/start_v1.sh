#!/usr/bin/env bash

echo '>>> STARTING SSH SERVER...'
/usr/sbin/sshd -D 2>&1 &

mig=$1

/usr/local/bin/confd -onetime -backend env

cd $DJANGO_PROJECT_HOME/djangoReq


if [[ $mig == 'true' ]]
then
  cd $DJANGO_PROJECT_HOME
  python3.7 manage.py migrate
  exit 0
fi

#a2enmod proxy
#a2enmod proxy_http
#a2enmod ssl
#a2enmod headers
#a2ensite deviare.conf
#a2ensite 000-default.conf
cd $DJANGO_PROJECT_HOME
python3.7 manage.py runserver 0.0.0.0:8080 > ./output.log