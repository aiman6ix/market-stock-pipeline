from datetime import datetime,timedelta
from airflow import DAG
import os
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator

default_args={                      #applies all parameters to every operator instead of writing it indivigually
    'owner':'aiman',
    'retries':1,
    'retry_delay':timedelta(minutes=5)
}

with DAG(
    default_args = default_args,
    dag_id='market_stock_etl_pipeline',
    description='This is a one way pipeline that transfers various stock information to our AWS S3 cloud stoarage',
    schedule = "@daily",        #Our pipeline to tranfer that data daily
    start_date=datetime(2026,7,14),
    catchup = False 
    ) as my_dag:    

 #creating SQL table to match our Dataframe column ifnromation
    load_to_progres = SQLExecuteQueryOperator(
        task_id='load_market_data_to_postgres',    #unique name of this specific step
        conn_id='postgres_default',                #connection identifier  (uses conn_id string to fetch connection detials from airflow systems)
        sql="""
            CREATE TABLE IF NOT EXISTS market_data (
                "Datetime" TIMESTAMP,
                "Close" NUMERIC(12,4),
                "High" NUMERIC(12,4),
                "Low" NUMERIC(12,4),
                "Open" NUMERIC(12,4),
                "Volume" NUMERIC(12,4),
                "Extracted_at" TIMESTAMP,
                ticker varchar(255),
                PRIMARY KEY ("Datetime",ticker)
            );

            """,
    )
#DockerOperator

    run_etl_container = DockerOperator(
        task_id = 'run_stock_etl',
        image = 'market-etl-app:latest',
        docker_url='unix://var/run/docker.sock',
        auto_remove = True,
        mount_tmp_dir=False,
        environment={           #Information gets sent transfered to AWS using my AWS information 
            'AWS_ACCESS_KEY_ID': os.environ.get('AWS_ACCESS_KEY_ID'),
            'AWS_SECRET_ACCESS_KEY': os.environ.get('AWS_SECRET_ACCESS_KEY'),
            'AWS_BUCKET_NAME':'toronto-transit-market-data-pipeline'
        }
    )

   
    run_etl_container >> load_to_progres    

