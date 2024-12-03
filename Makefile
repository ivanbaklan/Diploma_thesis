PROJECT_DIR ?= UrbanDjango

run:
	cd $(PROJECT_DIR) && python manage.py migrate
	cd $(PROJECT_DIR) && python manage.py runserver
lint:
	cd $(PROJECT_DIR) && black .

isort:
	cd $(PROJECT_DIR) && isort .

format: lint isort
	echo "Done"