dev:
	poetry run python manage.py runserver

lint:
	poetry run flake8 task_manager

isort:
	poetry run isort task_manager

test:
	poetry run python manage.py test

migrate:
	poetry run python manage.py migrate

start: migrate
	poetry run gunicorn task_manager.wsgi