#!/bin/bash
set -ex

cd /srv/cloudplayer
python3.6 -m venv --upgrade --copies .
bin/pip3.6 install --upgrade pip
bin/pip3.6 install -e .
