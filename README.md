# Products Showcase [API]
[![pipeline status](https://gitlab.com/alex9446/products-showcase_api/badges/dev/pipeline.svg)][jobs]
[![coverage report](https://gitlab.com/alex9446/products-showcase_api/badges/dev/coverage.svg)][jobs]

Main repository: https://gitlab.com/alex9446/products-showcase_api

dev branch deploy: https://products-showcase.herokuapp.com/products

## Short description
Server side REST API service for a products virtual showcase. \
Made for educational purposes for the study of python and flask.

## Installation
Some dependencies are needed, use requirements.txt to install them
```
pip install -r requirements.txt
```

## Usage
```
python server.py
# or
gunicorn wsgi:app --log-file -
```

[jobs]: https://gitlab.com/alex9446/products-showcase_api/-/jobs
