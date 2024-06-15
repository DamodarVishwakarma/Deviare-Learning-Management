#!/usr/bin/env bash

set -e

cp -f /root/.ssh/keys/* /root/.ssh/ || echo 'No pre-populated ssh keys!'


if [ ! -f "/root/.ssh/id_rsa.pub" ] && [ ! -f "/root/.ssh/id_rsa" ]; then
    echo ">>>  There are no ssh keys - SSH daemon can not be enabled!"
    exit 1
fi

chmod 600 -R /root/.ssh/id_rsa

mkdir -p /var/run/sshd && sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd
#sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd
echo "export VISIBLE=now" >> /etc/profile
echo "IdentityFile ~/.ssh/id_rsa" >> /etc/ssh/ssh_config
cat /root/.ssh/id_rsa.pub >> /root/.ssh/authorized_keys


