#!/bin/bash
set -ex
cd /var/www/api
python3 -m venv --upgrade --copies .
bin/pip install -e .
