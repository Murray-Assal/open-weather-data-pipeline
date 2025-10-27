#!/bin/bash
set -e

PROJECT_NAME="open-weather-data-pipeline"
mkdir -p ./{dags,logs,plugins,pgdata}

# -------------------------------
# Dockerfile
# -------------------------------
cat > Dockerfile <<'EOF'
FROM apache/airflow:3.0.1-python3.11

USER root
RUN apt-get update && apt-get install -y \
    libpq-dev build-essential && \
    apt-get clean

USER airflow
RUN pip install --no-cache-dir psycopg2-binary pandas sqlalchemy

COPY dags/ /opt/airflow/dags/
COPY plugins/ /opt/airflow/plugins/
EOF

# -------------------------------
# docker-compose.yml
# -------------------------------
cat > docker-compose.yml <<'EOF'
version: '3.9'

services:
  postgres:
    image: postgres:15
    container_name: postgres
    environment:
      POSTGRES_USER: airflow
      POSTGRES_PASSWORD: airflow
      POSTGRES_DB: airflow
    ports:
      - "5433:5432"
    volumes:
      - ./pgdata:/var/lib/postgresql/data

  airflow:
    build: .
    container_name: airflow
    depends_on:
      - postgres
    environment:
      AIRFLOW__CORE__EXECUTOR: LocalExecutor
      AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres:5432/airflow
      AIRFLOW__CORE__FERNET_KEY: "ZmFrZV9mZXJuZXRfa2V5X2Zvcl9kZW1v"
      AIRFLOW__CORE__LOAD_EXAMPLES: "false"
    volumes:
      - ./dags:/opt/airflow/dags
      - ./logs:/opt/airflow/logs
      - ./plugins:/opt/airflow/plugins
    ports:
      - "8080:8080"
    command: >
      bash -c "
        airflow db upgrade &&
        airflow users create --username admin --password admin
          --firstname Air --lastname Flow --role Admin --email admin@example.com &&
        airflow webserver & airflow scheduler
      "
EOF

# -------------------------------
# Sample DAG: simple_etl_pipeline
# -------------------------------
cat > dags/etl_pipeline.py <<'EOF'
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd
import psycopg2

def extract(**kwargs):
    data = pd.DataFrame({
        "id": [1, 2, 3],
        "value": ["A", "B", "C"]
    })
    data.to_csv('/tmp/extracted.csv', index=False)

def transform(**kwargs):
    df = pd.read_csv('/tmp/extracted.csv')
    df['value'] = df['value'].str.lower()
    df.to_csv('/tmp/transformed.csv', index=False)

def load(**kwargs):
    conn = psycopg2.connect(
        host="postgres",
        dbname="airflow",
        user="airflow",
        password="airflow"
    )
    cur = conn.cursor()
    df = pd.read_csv('/tmp/transformed.csv')
    cur.execute("CREATE TABLE IF NOT EXISTS etl_data (id INT, value TEXT);")
    for _, row in df.iterrows():
        cur.execute("INSERT INTO etl_data (id, value) VALUES (%s, %s);", (row.id, row.value))
    conn.commit()
    cur.close()
    conn.close()

default_args = {"owner": "airflow", "start_date": datetime(2025, 10, 1)}

with DAG("simple_etl_pipeline", default_args=default_args, schedule_interval="@daily", catchup=False) as dag:
    t1 = PythonOperator(task_id="extract", python_callable=extract)
    t2 = PythonOperator(task_id="transform", python_callable=transform)
    t3 = PythonOperator(task_id="load", python_callable=load)
    t1 >> t2 >> t3
EOF

# -------------------------------
# Final Message
# -------------------------------
echo "✅ Project structure ready: $PROJECT_NAME"
echo
echo "Next steps:"
echo "-----------------------------------------"
echo "1. cd $PROJECT_NAME"
echo "2. docker build -t airflow-etl:latest ."
echo "3. docker compose up -d"
echo
echo "Then visit Airflow UI → http://localhost:8080"
echo "Username: admin | Password: admin"
echo "-----------------------------------------"
