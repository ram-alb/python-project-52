install:
	poetry install

lint:
	poetry run flake8 task_manager

test:
	poetry run coverage run manage.py test

test-coverage:
	poetry run coverage report

selfcheck:
	poetry check

check: selfcheck test lint

isort:
	poetry run isort task_manager

migrate:
	poetry run python manage.py migrate

shell:
	poetry run python manage.py shell_plus --ipython

dev:
	poetry run python manage.py runserver

start:
	poetry run gunicorn task_manager.wsgi