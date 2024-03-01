dev:
	poetry run flask --app page_analyzer:app run
build:
	poetry build
install:
	poetry install
lint:
	poetry run flake8 gendiff
PORT ?= 8000
start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app
selfcheck:
	poetry check
check: selfcheck lint