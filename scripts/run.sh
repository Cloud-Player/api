#!/bin/bash

supervisorctl start api
service nginx reload
