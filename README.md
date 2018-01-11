[![Build Status](https://travis-ci.org/Cloud-Player/api.svg?branch=master)](https://travis-ci.org/Cloud-Player/api)
[![API Documentation](https://img.shields.io/badge/raml-valid-brightgreen.svg)](https://cloud-player.github.io/api)
[![Code Coverage](https://codecov.io/gh/Cloud-Player/api/branch/master/graph/badge.svg)](https://codecov.io/gh/Cloud-Player/api)
  
# Cloud Player API

## install
```
python3 -m venv --upgrade --copies .
bin/pip3 install -e .
```

## develop
```
bin/api
open http://localhost:8040
```

## test
```
bin/pip install -e .[test]
bin/test
```
