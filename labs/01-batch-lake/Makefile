test:
	pytest -q test_app.py
local:
	mkdir -p output && python app.py
docker:
	docker build -t batch-lake . && docker run --rm -v "$$(pwd)/output:/app/output" batch-lake

