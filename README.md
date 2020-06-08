# `elizabeth-cabell-fine-art-api`
[![Build Status](https://travis-ci.com/cabellwg/elizabeth-cabell-fine-art-api.svg?token=LKSsVQYJaBXGxfgSBjEE&branch=master)](https://travis-ci.com/cabellwg/elizabeth-cabell-fine-art-api)
[![Coverage Status](https://coveralls.io/repos/github/cabellwg/elizabeth-cabell-fine-art-api/badge.svg?branch=master)](https://coveralls.io/github/cabellwg/elizabeth-cabell-fine-art-api?branch=master)
[![Python version](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/)
[![Flask version](https://img.shields.io/badge/flask-1.1.2-777.svg)](https://flask.pocoo.org/)

> Flask API to interact with art database.

### Environment variables

Required in production env

- `SECRET_KEY_SECRET`: The name of the secret where the application secret key is stored
- `JWT_SECRET_KEY_SECRET`: The name of the secret where the JWT secret key is stored
- `DB_PASS_SECRET`: The name of the secret where the database password is stored
- `IMAGE_STORE_DIR`: The name of the directory where the image store volume is mounted
