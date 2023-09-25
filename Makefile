SHELL := /bin/bash

prepare : 
	@echo "Prepare"
	python3 -m pip install virtualenv
	python3 -m venv .venv/

install : prepare
	@echo "Install"
	source .venv/bin/activate && \
		python -m pip install -r requirements.txt

verify : install
	source .venv/bin/activate && \
		flake8 . --extend-exclude=dist,build --show-source --statistics

test : 
	@echo "Test"

run : 
	@echo "Run"
