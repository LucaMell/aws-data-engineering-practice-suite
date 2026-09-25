FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN useradd --uid 1000 --create-home app

COPY src ./src
COPY tests ./tests
COPY sample ./sample
COPY schemas ./schemas

RUN chown -R app:app /app

USER app

CMD ["python", "-m", "pytest", "-q", "tests"]
