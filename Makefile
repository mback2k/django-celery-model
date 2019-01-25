all: Pipfile.lock dev-requirements.txt

Pipfile.lock: Pipfile
	pipenv lock --pre --dev

dev-requirements.txt: Pipfile Pipfile.lock
	pipenv lock --pre --dev --requirements > dev-requirements.txt

build: setup.py
	pipenv run python3 setup.py sdist bdist_wheel

publish: dist
	pipenv run twine upload -s -i 2BCE098759303489D895D61D128358963026398E dist/*
