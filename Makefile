SHELL := /bin/bash

help:
	@echo "usage:"
	@echo "    make docs    -- setup and serve docs locally"
	@echo "    make release -- build and release to PyPI"

docs:
	pip install -r doc/requirements.txt
	mkdocs serve

release:
	rm -rf dist/*
	python setup.py register bdist_wheel sdist
	twine upload dist/*
