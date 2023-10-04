SHELL := /bin/bash

prepare : 
	@echo "Prepare"
	python3 -m pip install virtualenv
	python3 -m venv .venv/

install : prepare
	@echo "Install"
	source .venv/bin/activate && \
	python -m pip install --upgrade pip && \
	python -m pip install -r requirements.txt
	if [[ $${EUID} > 0 ]]; then sudo apt-get install -y sqlite3 xmlstarlet; else apt-get install -y sqlite3 xmlstarlet; fi

verify : install
	source .venv/bin/activate && \
		flake8 . --extend-exclude=dist,build --show-source --statistics

coverage : install
	source .venv/bin/activate && \
		export SQLITE_DB_FILE="$$(pwd)/tests/data/test_data.db" && \
		coverage run -m pytest -s -v tests/*_test.py --html=report.html --self-contained-html

format : install
	source .venv/bin/activate && \
		for target in `find  -name *.py -not -path "./.venv/*" -not -path "./.venv-old/*"`; do autopep8 $$target; done

unit-test : install
	source .venv/bin/activate && \
		export SQLITE_DB_FILE="$$(pwd)/tests/data/test_data.db" && \
		python -m pytest -v tests/*_test.py  --junitxml=test-reports/report.xml

acceptance-test : install
	source .venv/bin/activate && \
		export SQLITE_DB_FILE="$$(pwd)/tests/data/test_data.db" && \
		python -m pytest -v bdd/ --junitxml=${REPORT_FILE}

run : 
	source .venv/bin/activate && \
		export SQLITE_DB_FILE="$$(pwd)/tests/data/test_data.db" && \
		python -m lib.backtest.runner lib.strategies dummy DummyStrategy

pull : install
	source .venv/bin/activate && \
	source .env.test && \
	export SQLITE_DB_FILE="$$(pwd)/tests/data/test_data.db" && \
	python -m script.alpaca_market_data_pull

store: install
	source .venv/bin/activate && \
	source .env.prod && \
	export SQLITE_DB_FILE="$$(pwd)/data/stock_data.db" && \
	sqlite3 $$SQLITE_DB_FILE < ./.tmp/`ls -1 .tmp/|grep ALL_SYM`


.PHONY: clean
clean :
	rm -rf .pytest_cache/ .venv/ test-reports/ .pytest_cache/

