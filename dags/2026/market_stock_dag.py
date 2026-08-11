import sys
import os

sys.path.insert(0, '/opt/airflow')

from src.extractor import run_market_etl
from src.loader import run_loader
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime,  timedelta

default_args = {
        'owner' :'aiman',
        'depends_on_past' : False,
        'start_date' : datetime(2026,8,1),
        'retries' : 1,
        'retry_delay' : timedelta(minutes=5)
}

with DAG(
    dag_id='market_stock_pipeline',
    default_args = default_args,
    description='ETL pipeline for market stock data',
    schedule="0 9 * * 1-5 ",     #runs at 9 am est till market closure from monday through friday
    catchup = False
        ) as dag:

    task_extract_to_s3 = PythonOperator(
        task_id='extract_and_upload_to_s3',
        python_callable=run_market_etl
    )

    task_load_to_postgres= PythonOperator(
        task_id='download_and_upload_to_postgres',
        python_callable=run_loader
    )

    task_extract_to_s3 >> task_load_to_postgres