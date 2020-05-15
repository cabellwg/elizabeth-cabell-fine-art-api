#!/usr/bin/python

import sys
import logging

from flask_app import create_app


logging.basicConfig(stream=sys.stderr)

application = create_app()
