PROJECT_DIR ?= contextly
install:
	python -m ensurepip --upgrade
	python -m pip install --upgrade setuptools
    pip install uv
	pip install -r requirements.txt
run:
	echo "install"
lint:
	echo "Start lint"
	cd $(PROJECT_DIR) && black .

isort:
	echo "Start isort"
	cd $(PROJECT_DIR) && black .

format: lint isort
	echo "Format Done"