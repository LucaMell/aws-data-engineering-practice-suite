FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir dbt-redshift
COPY . .
CMD ["dbt","build","--profiles-dir","."]

