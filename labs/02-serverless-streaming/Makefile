test:
	pytest -q test_handler.py
local:
	python -m json.tool sample/events.jsonl >/dev/null || true
docker:
	docker build -t serverless-stream .

