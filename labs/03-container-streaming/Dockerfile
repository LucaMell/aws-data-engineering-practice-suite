FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir boto3
COPY worker.py .
RUN useradd --create-home app
USER app
CMD ["python","worker.py"]

