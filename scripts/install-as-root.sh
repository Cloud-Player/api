#!/bin/bash
set -ex
id -u cloudplayer &>/dev/null || useradd -m -U -d /srv/cloudplayer cloudplayer
apt-get update
sudo apt-get install -y redis-server supervisor nginx
