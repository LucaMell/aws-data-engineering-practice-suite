.RECIPEPREFIX := >

PYTHON ?= python
IMAGE_NAME ?= secure-s3-file-ingestion:local

.PHONY: test docker-build docker-run

test:
>$(PYTHON) -m pytest -q tests

docker-build:
>docker build --tag $(IMAGE_NAME) .

docker-run:
>docker run --rm --network none $(IMAGE_NAME)
