#!/bin/bash
set -ex

# create cloudplayer service user
id -u cloudplayer &> /dev/null || useradd -m -U -d /srv/cloudplayer cloudplayer

# update and install dependencies
apt-get update
apt-get install -y \
redis-server \
supervisor \
nginx \
python3-venv \
python3-pycurl \
python3-dev \
libcurl4-openssl-dev \
libssl-dev \
postgresql

# disable default nginx site
rm /etc/nginx/sites-enabled/default &> /dev/null || echo "default disabled"
