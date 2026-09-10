FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends default-jre-headless && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir boto3 amazon-kclpy
COPY record_processor.py kcl.properties ./
RUN useradd --create-home app
USER app
CMD amazon_kclpy_helper.py --print_command --java /usr/bin/java --properties kcl.properties | sh
