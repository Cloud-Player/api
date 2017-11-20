#!/bin/bash
set -ex
id -u cloudplayer &>/dev/null || useradd -m -U -d /srv/cloudplayer cloudplayer
apt-get update
apt-get install -y \
redis-server \
supervisor \
nginx \
python3-venv \
python3-pycurl \
python3-dev \
libcurl4-openssl-dev \
libssl-dev
