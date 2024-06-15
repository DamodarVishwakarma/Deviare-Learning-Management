#!/usr/bin/env bash

mig=$1

# /usr/local/bin/confd -onetime -backend env
/usr/sbin/service nginx start
cd $DJANGO_PROJECT_HOME


if [[ $mig == 'true' ]]
then
  cd $DJANGO_PROJECT_HOME
  python3.7 manage.py migrate
  exit 0
fi
echo '>>> STARTING SSH SERVER...'
/usr/sbin/sshd -D 2>&1 &


/usr/sbin/service nginx restart >&1 &
cd $DJANGO_PROJECT_HOME
python3.7 manage.py runserver 0.0.0.0:8080 > ./output.log