FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN useradd --uid 1000 --create-home app

COPY evaluate.py .
COPY run_sql_checks.py .
COPY quality.sql .
COPY sample ./sample

RUN mkdir -p /app/output \
    && chown app:app /app/output

USER app

CMD ["python", "run_sql_checks.py", "--output", "/app/output"]
