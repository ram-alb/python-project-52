dev:
	poetry run python manage.py runserver

lint:
	poetry run flake8 task_manager

isort:
	poetry run isort task_manager

start:
	poetry run gunicorn task_manager.wsgi