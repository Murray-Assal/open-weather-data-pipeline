from airflow.sdk import task, dag
from airflow.providers.http.hooks.http import HttpHook
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime, timedelta
from airflow.models import Variable
from psycopg2.extras import execute_values
import pandas as pd
import logging

lat=30.044420 # Latitude for Cairo, Egypt
lon=31.235712 # Longitude for Cairo, Egypt
api_key=Variable.get("open_weather_map_api_key") # Replace with your OpenWeatherMap API key

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(seconds=10),
}
@dag(
    dag_id='open_weather_map_dag',
    default_args=default_args,
    description='A DAG to fetch weather data from OpenWeatherMap API and store it in PostgreSQL',
    schedule='@weekly',
    start_date=datetime(2025, 10, 28),
    catchup=False,
)
def open_weather_map_dag():

    @task()
    def extract_weather_data():
        '''
        Extract weather data from OpenWeatherMap API for the specified location for the last 5 days.
        The input data should look similar to this:
        {
            "lat": 30.0444,
            "lon": 31.2357,
            "timezone": "Africa/Cairo",
            "timezone_offset": 7200,
            "data":
            [
                {
                    "dt": 1622505600,
                    "sunrise": 1622516073,
                    "sunset": 1622566295,
                    "temp": 22.52,
                    "feels_like": 22.29,
                    "pressure": 1011,
                    "humidity": 56,
                    "dew_point": 13.31,
                    "clouds": 0,
                    "visibility": 6000,
                    "wind_speed": 5.66,
                    "wind_deg": 20,
                    "weather": [
                        {
                            "id": 800,
                            "main": "Clear",
                            "description": "clear sky",
                            "icon": "01n"
                        }
                    ]
                }
            ]
        }
        '''
        http_hook = HttpHook(method='GET', http_conn_id='open_weather_map_api')
        weather_data = []
        start_date = datetime.now() - timedelta(days=5)
        end_date = datetime.now()
        delta = timedelta(days=1)
        date_in_loop = start_date
        while date_in_loop <= end_date:
            timestamp = int(date_in_loop.timestamp())
            endpoint = f'/data/3.0/onecall/timemachine?lat={lat}&lon={lon}&dt={timestamp}&appid={api_key}&units=metric'
            response = http_hook.run(endpoint)
            if response.status_code == 200:
                data = response.json()
                weather_data.append(data)
                logger.info(f"Extracted weather data for {date_in_loop.strftime('%Y-%m-%d')}")
            else:
                logger.error(f"Failed to fetch data for {date_in_loop.strftime('%Y-%m-%d')}: {response.text}")
                raise Exception("API request failed")
            date_in_loop += delta
        return weather_data

    
    @task()
    def transform_and_load_weather_data(weather_data):
        # Transform the extracted data into a pandas DataFrame
        records = []
        for entry in weather_data:
            record = {
                'timezone': entry['timezone'],
                'sunrise': datetime.fromtimestamp(entry['data'][0]['sunrise']),
                'sunset': datetime.fromtimestamp(entry['data'][0]['sunset']),
                'temp': entry['data'][0]['temp'],
                'feels_like': entry['data'][0]['feels_like'],
                'pressure': entry['data'][0]['pressure'],
                'humidity': entry['data'][0]['humidity'],
                'dew_point': entry['data'][0]['dew_point'],
                'clouds': entry['data'][0]['clouds'],
                'visibility': entry['data'][0]['visibility'],
                'wind_speed': entry['data'][0]['wind_speed'],
                'wind_deg': entry['data'][0]['wind_deg'],
                'sky': entry['data'][0]['weather'][0]['description']
            }
            records.append(record)
        weather_df = pd.DataFrame(records)
        logger.info("Transformed weather data into DataFrame")

        # Load the transformed data into PostgreSQL
        pg_hook = PostgresHook(postgres_conn_id='postgres_database')
        conn = pg_hook.get_conn()
        cursor = conn.cursor()
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS cairo_weather_data (
            id SERIAL PRIMARY KEY,
            timezone VARCHAR(50),
            sunrise TIMESTAMP,
            sunset TIMESTAMP,
            temp FLOAT,
            feels_like FLOAT,
            pressure INT,
            humidity INT,
            dew_point FLOAT,
            clouds INT,
            visibility INT,
            wind_speed FLOAT,
            wind_deg INT,
            sky VARCHAR(100),
            CONSTRAINT unique_sunrise UNIQUE (timezone, sunrise)
            );
        '''
        cursor.execute(create_table_query)
        conn.commit()

        insert_query = '''
            INSERT INTO cairo_weather_data (
                timezone, sunrise, sunset, temp, feels_like,
                pressure, humidity, dew_point, clouds,
                visibility, wind_speed, wind_deg, sky
            ) VALUES %s
            ON CONFLICT (timezone, sunrise) DO NOTHING;
            '''

        values = [tuple(x) for x in weather_df.to_numpy()]
        execute_values(cursor, insert_query, values)
        conn.commit()
        cursor.close()
        conn.close()
        logger.info("Loaded weather data into PostgreSQL")

    weather_data = extract_weather_data()
    transform_and_load_weather_data(weather_data)
open_weather_map_dag = open_weather_map_dag()