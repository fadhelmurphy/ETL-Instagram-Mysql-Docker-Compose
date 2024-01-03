from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
import os

def run_scraper():
    os.system("python scraper.py")

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'scrape_instagram',
    default_args=default_args,
    description='Scrape Instagram every 4 minutes',
    schedule_interval='*/4 * * * *',  # Menjalankan setiap 4 menit
)

run_this = PythonOperator(
    task_id='run_scraper_task',
    python_callable=run_scraper,
    dag=dag,
)
