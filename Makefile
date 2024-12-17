PROJECT_DIR ?= contextly
install:
	echo "Install"
	python -m ensurepip --upgrade
	python -m pip install --upgrade setuptools
	pip install uv
	uv sync
run:
	echo "Run"
	uvicorn contextly.main:app --host 0.0.0.0 --port 8080 --workers 1 --reload
lint:
	echo "Start lint"
	cd $(PROJECT_DIR) && black .

isort:
	echo "Start isort"
	cd $(PROJECT_DIR) && isort .

format: lint isort
	echo "Format Done"
test:
	echo "Run tests"
	export PYTHONPATH=$(shell pwd) && pytest -v
docker:
	echo "Docker build"
	docker -l info build -t contextly .
docker_run:
	echo "Docker run"
	docker run -d -p 8080:8080 --name my-contextly contextly
