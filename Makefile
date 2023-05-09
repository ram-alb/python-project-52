dev:
	poetry run python manage.py runserver

lint:
	poetry run flake8 task_manager

isort:
	poetry run isort task_manager

test:
	poetry run python manage.py test

selfcheck:
	poetry check

check: selfcheck test lint

migrate:
	poetry run python manage.py migrate

start:
	poetry run gunicorn task_manager.wsgi