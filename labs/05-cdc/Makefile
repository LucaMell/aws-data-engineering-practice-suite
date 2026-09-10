test:
	pytest -q test_sql.py
local:
	docker compose up --build -d
	curl -X POST -H 'Content-Type: application/json' --data @register-connector.json http://localhost:8083/connectors

