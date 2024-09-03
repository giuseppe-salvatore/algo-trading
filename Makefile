SHELL := /bin/bash

all: install format verify unit-test acceptance-test  

prepare: 
	@echo "Prepare"
	python3 -m pip install virtualenv
	python3 -m venv .venv/

install: prepare
	@echo "Install"
	source .venv/bin/activate && \
	python -m pip install --upgrade pip && \
	python -m pip install -r requirements.txt
	if [[ $${EUID} > 0 ]]; \
	then \
		xargs sudo DEBIAN_FRONTEND=noninteractive apt-get install -y < requirements-deb.txt > /dev/null;\
	else \
		xargs DEBIAN_FRONTEND=noninteractive apt-get install -y < requirements-deb.txt > /dev/null;\
	fi
	source .venv/bin/activate && pre-commit install

verify:
	source .venv/bin/activate && \
	flake8 . --extend-exclude=dist,build --show-source --statistics

coverage:
	source .venv/bin/activate && \
	export SQLITE_DB_FILE="$$(pwd)/tests/data/test_data.db" && \
	coverage run -m pytest -s -v tests/*_test.py -v bdd/scenarios/* --html=report.html --self-contained-html && \
	coverage report

format:
	source .venv/bin/activate && \
	for target in `find  -name *.py -not -path "./.venv/*"`; do autopep8 -i $$target; done

unit-test:
	source .venv/bin/activate && \
	export SQLITE_DB_FILE="$$(pwd)/tests/data/test_data.db" && \
	python -m pytest -v tests/*_test.py  --junitxml=test-reports/report.xml

acceptance-test:
	source .venv/bin/activate && \
	export SQLITE_DB_FILE="$$(pwd)/tests/data/test_data.db" && \
	python -m pytest -v bdd/scenarios/* --junitxml=${REPORT_FILE}

test: 
	source .venv/bin/activate && \
	export SQLITE_DB_FILE="$$(pwd)/tests/data/test_data.db" && \
	python -m lib.backtest.runner lib.strategies dummy DummyStrategy

run-dummy:
	source .venv/bin/activate && \
	source .env.prod && \
	python -m lib.backtest.runner --config-file samples/config-dummy.yaml --log-level INFO

run-macrossover:
	source .venv/bin/activate && \
	source .env.prod && \
	python -m lib.backtest.runner --config-file samples/config-macrossover.yaml --log-level INFO

pull-alpaca: install
	source .venv/bin/activate && \
	source .env.prod && \
	python -m script.alpaca_market_data_pull

pull-alphavantage: install
	source .venv/bin/activate && \
	source .env.prod && \
	export SQLITE_DB_FILE="$$(pwd)/tests/data/test_data.db" && \
	python -m lib.market_data_provider.alphavantage "2014-10" "2014-01"

store-all: install
	source .venv/bin/activate && \
	source .env.prod && \
	export SQLITE_DB_FILE="$$(pwd)/data/stock_data.db" && \
	sqlite3 $$SQLITE_DB_FILE < ./.tmp/`ls -1 .tmp/|grep ALL_SYMBOLS`

store-alphavantage: install
	source .venv/bin/activate && \
	export SQLITE_DB_FILE="$$(pwd)/data/stock_data.alphavantage.db" && \
	for sql_file in `ls -1 ./data/alphavantage/sql/`; \
	do \
		echo "Storing $$sql_file in $$SQLITE_DB_FILE"; \
		sqlite3 $$SQLITE_DB_FILE < ./data/alphavantage/sql/$$sql_file; \
	done;

store-alpaca: install
	source .venv/bin/activate && \
	export SQLITE_DB_FILE="$$(pwd)/data/stock_data.alpaca.db" && \
	for sql_file in `ls -1 ./data/alpaca/sql/`; \
	do \
		echo "Storing $$sql_file in $$SQLITE_DB_FILE"; \
		sqlite3 $$SQLITE_DB_FILE < ./data/alpaca/sql/$$sql_file; \
	done;

store-single: install
	source .venv/bin/activate && \
	source .env.prod && \
	export SQLITE_DB_FILE="$$(pwd)/data/stock_data.db" && \
	for f in `ls -1 .tmp/|grep sql`; do echo "process $$f"; sqlite3 $$SQLITE_DB_FILE < ./.tmp/$$f; done;

db-info-alpaca: install
	source .venv/bin/activate && \
	source .env.prod && \
	export SQLITE_DB_FILE="$$(pwd)/data/stock_data.alpaca.db" && \
	python -m script.get_cache_period

db-info-alphavantage: install
	source .venv/bin/activate && \
	source .env.prod && \
	export SQLITE_DB_FILE="$$(pwd)/data/stock_data.alphavantage.db" && \
	python -m script.get_cache_period

# Note, this should only be running on silver-boxy
make-monthly-update:
	bash script/pull-previous-month-data.sh && \
	bash script/sync-data-with-dark-matter.sh; \

.PHONY: clean hard-clean
clean :
	rm -rf .pytest_cache/ test-reports/ .pytest_cache/
	rm -rf .tmp/*

hard-clean:
	rm -rf .venv/

