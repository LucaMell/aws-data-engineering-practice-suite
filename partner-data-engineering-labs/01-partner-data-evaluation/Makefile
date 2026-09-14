.RECIPEPREFIX := >

PYTHON ?= python
IMAGE_NAME ?= partner-data-evaluation:local

.PHONY: test local sql docker-build docker-run

test:
>$(PYTHON) -m pytest -q tests/test_evaluate.py

local:
>$(PYTHON) evaluate.py

sql:
>$(PYTHON) run_sql_checks.py

docker-build:
>docker build --tag $(IMAGE_NAME) .

docker-run:
>mkdir -p output
>docker run --rm --network none \
>  --mount "type=bind,source=$(CURDIR)/output,target=/app/output" \
>  $(IMAGE_NAME)
