#!/bin/bash
set -ex

# create cloudplayer service user
id -u cloudplayer &> /dev/null || useradd -m -U -d /srv/cloudplayer cloudplayer

# update and install dependencies
add-apt-repository -y \
ppa:jonathonf/python-3.6
apt-get update
apt-get install -y \
redis-server \
supervisor \
nginx \
htop \
python3.6 \
python3.6-venv \
python3.6-dev \
python3-pycurl \
python-pip \
python-pip-whl \
libcurl4-openssl-dev \
libssl-dev \
postgresql

# disable default nginx site
rm /etc/nginx/sites-enabled/default &> /dev/null || echo "default disabled"
