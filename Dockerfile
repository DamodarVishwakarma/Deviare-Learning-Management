FROM ubuntu:18.04
RUN apt-get update && apt-get install -y software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa

RUN apt-get update && apt-get install -y apache2\
    python3.7\
    python3.7-dev\
    python3-pip\
    libapache2-mod-wsgi-py3\
    build-essential\
    libmysqlclient-dev\
    mysql-client\
    wget \
    libcairo2 \ 
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev\
    shared-mime-info

RUN rm -f /var/log/apache2/access.log
RUN rm -f /var/log/apache2/error.log
RUN ln -s /dev/stderr /var/log/apiserver.log
RUN ln -s /dev/stderr /var/log/apache2/error.log
# RUN mkdir -p /etc/apache2/FormFiller
# RUN chown -R www-data:www-data /etc/apache2/FormFiller/
RUN chown -R www-data:www-data /etc/apache2/sites-available/
RUN  apt-get update && apt-get install -y apache2 libapache2-mod-wsgi-py3
COPY requirements.txt /
RUN python3.7 -m pip install requests
RUN python3.7 -m pip install -r /requirements.txt

COPY . /backend/
RUN mkdir -p /backend/static
RUN cd /backend/ && python3.7 manage.py collectstatic --noinput
RUN cp -r /backend/admin /backend/static


COPY docker/backend/deviare.wsgi /
COPY docker/backend/deviare.conf /etc/apache2/sites-available/
COPY docker/backend/ports.conf /etc/apache2/

RUN chmod 777 /deviare.wsgi
RUN touch /tmp/apiserver.log
RUN chmod -R 777 /tmp/

ADD docker/backend/confd-0.14.0-linux-amd64 /usr/local/bin/confd
RUN chmod +x /usr/local/bin/confd
ADD docker/backend/confd /etc/confd

RUN apt-get update
RUN apt-get install -y openssh-server 
RUN apt-get install -y redis-server 
################### SSH Daemon #############
COPY docker/backend/ssh/ /root/.ssh/
COPY docker/backend/app /app
RUN chmod +x /app/bin/*
RUN mkdir /var/run/sshd
RUN /app/bin/entrypoint.sh

COPY docker/backend/start.sh /
RUN chmod +x /start.sh

EXPOSE 8080
EXPOSE 80
EXPOSE 22

ENTRYPOINT /bin/bash /start.sh ${MIGRATE}
