#!/bin/bash
set -ex
cd /srv/cloudplayer/api
python3 -m venv --upgrade --copies .
bin/pip install -e .
