#!/bin/bash
set -ex
apt-get update
sudo apt-get install -y redis-server supervisor nginx
