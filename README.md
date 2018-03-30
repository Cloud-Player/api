[![Build Status](https://travis-ci.org/Cloud-Player/api.svg?branch=master)](https://travis-ci.org/Cloud-Player/api)
[![Openapi Documentation](https://img.shields.io/badge/doc-openapi-brightgreen.svg)](https://cloud-player.github.io/api/restapi.html)
[![Asyncapi Documentation](https://img.shields.io/badge/doc-asyncapi-brightgreen.svg)](https://cloud-player.github.io/api/asyncapi.html)
[![Code Coverage](https://codecov.io/gh/Cloud-Player/api/branch/master/graph/badge.svg)](https://codecov.io/gh/Cloud-Player/api)
[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads)

# Cloud Player API

This repository contains the REST and ASYNC backend API for the Cloud-Player
web and desktop applications. It is build using the tornado framework and integrates
a PostgreSQL database over SQLAlchemy. The pub/sub system is implemented with Redis.
There is a continuous testing and deployment toolchain setup with travis and AWS.

## require

```
python==3.6
pip>=9
npm>=3.5
postgresql>=10
redis>=3
```

## install
```
make
```

## develop
```
bin/api
```

## test
```
bin/test
```
