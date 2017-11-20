#!/bin/bash
set -ex
cd /srv/cloudplayer
python3.5 -m venv --upgrade --copies .
bin/pip3.5 install --upgrade pip
bin/pip3.5 install -e .
