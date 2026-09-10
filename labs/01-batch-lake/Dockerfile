FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir pandas pyarrow
COPY . .
CMD ["python", "app.py"]

