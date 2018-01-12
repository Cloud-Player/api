#!/bin/bash
set -ex

supervisorctl start api
service nginx reload
