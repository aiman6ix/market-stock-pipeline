import boto3
import os
from dotenv import load_dotenv
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine,text
from sqlalchemy.engine import URL
ROOT_DIR = Path(__file__).resolve().parent.parent
env_path = ROOT_DIR / '.env'

load_dotenv(dotenv_path=env_path)      #loading info from our .env file

def run_loader():
        
        s3 = boto3.client(
            's3',
            aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
                        )
        bucket_name = 'toronto-transit-market-data-pipeline'
        #lists of obj inside the bucket
        response = s3.list_objects_v2(Bucket=bucket_name)
        #check the contents inside the object
        if 'Contents' in response:
            csv_file = [obj for obj in response['Contents'] if obj['Key'].endswith('.csv')]
            #print(f'all the csv files found in the bucket:{csv_file}')
            latest_file = None
            #Gets last modified csv file
            for obj in csv_file:    
                if latest_file is None or obj['LastModified'] > latest_file['LastModified']:
                    latest_file = obj
        if latest_file:
            latest_file_key = latest_file['Key']
        #Now we extract the .csv file from the AWS bucket
            local_file_name = './temp_latest.csv'
            s3.download_file(bucket_name,latest_file_key,local_file_name)
            df = pd.read_csv(local_file_name)
            print('preview of data')
            print(df.head())
        #Now we move on to building a PostgreSQL Engine
            url_object = URL.create(
                "postgresql+psycopg2",
                username=os.getenv('POSTGRES_USER') or 'airflow',
                password=os.getenv('POSTGRES_PASSWORD') or 'airflow',
                host=os.getenv('POSTGRES_HOST') or 'postgres',
                port=int(os.getenv('POSTGRES_PORTS') or 5432),
                database=os.getenv('POSTGRES_DB') or 'airflow',
            )
            engine = create_engine(url_object)
            """
            i wanted to verify the onnection worked, at first it didnt since we were missing a port , but after
            adding it in the .ymal file and in the .env, the conenction was established
            try:
                with engine.connect() as connection:
                    print("Successfully connected to PostgreSQL!")
            except Exception as e:
                    print(f"Failed to connect: {e}")
            """
            #Now i transfer the data from the Dataframe holding the .csv into our SQL database
            df.to_sql(name='stock_prices',con=engine,if_exists='append',index=False)
            print("Data successfully ingested into PostgreSQL!")
            """
            used this to test if the data was successfully transfered from .csv file to SQL talble
            with engine.connect() as connection:
                result = connection.execute(text("SELECT COUNT(*) FROM stock_prices;"))
                print(f"Total rows in table: {result.scalar()}")
            """
        """ Used this black of code to get the name of our bucket in the AWS cloud
        response = s3.list_buckets()
        
        for bucket in response['Buckets']:
            print(f'name of the bucket {bucket["Name"]}')
        """

if __name__ == "__main__":
    run_loader()