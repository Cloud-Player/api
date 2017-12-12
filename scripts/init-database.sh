#!/bin/bash
set -ex

psql -f /srv/cloudplayer/scripts/init-database.sql
