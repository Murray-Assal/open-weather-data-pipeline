FROM apache/airflow:3.0.1-python3.11

USER airflow

RUN pip install --no-cache-dir psycopg2-binary pandas sqlalchemy

COPY dags/ /opt/airflow/dags/
COPY plugins/ /opt/airflow/plugins/