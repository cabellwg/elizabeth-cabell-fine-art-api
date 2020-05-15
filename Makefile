init:
	pip3 install virtualenv;
	python3.8 -m virtualenv -p python3.8 p3_8env; \
	. ./p3_8env/bin/activate; \
	pip install -r requirements.txt

test:
	. ./p3_8env/bin/activate; \
	export ENV test; \
	coverage run --source flask_app -m unittest discover -vcs tests

dev:
	. ./p3_8env/bin/activate; \
	export ENV dev; \
	export FLASK_APP=flask_app; \
	export FLASK_ENV=development; \
	flask run

.PHONY: init test dev
