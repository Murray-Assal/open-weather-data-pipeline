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
