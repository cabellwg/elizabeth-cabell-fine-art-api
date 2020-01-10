#!/usr/bin/python

import sys
import logging
logging.basicConfig(stream=sys.stderr)

from flask_app import create_app
application = create_app()
