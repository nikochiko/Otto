.PHONY: run deps

run:
	venv/bin/python3 otto/app.py

deps: venv
	venv/bin/python3 -m pip install -r requirements.txt

venv:
	python3 -m venv venv
