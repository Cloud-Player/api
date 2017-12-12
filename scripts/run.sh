#!/bin/bash

supervisorctl update api
service nginx reload
