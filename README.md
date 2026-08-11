# Market Stock Data Pipeline

An automated ETL data pipeline deployed with Apache Airflow, Docker, AWS S3, and PostgreSQL to ingest historical market stock ticker data.

## Features
- Data process scheduling: Airflow DAGs function was used to process and track stock data coming in and out
- Cloud Storage: Processed data are sent to and extracted from to an AWS S3 bucket 
- Database Storage: Extracted .csv files from the cloud storage are turned into a pandas dataframe and written to a postgreSQL database
- Containerization: Containerized setup with a end-to-end daily local and production deployment

## Setup
1. Clone the repository.
2. In `.env`, replace with your AWS credentials (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`).
3. Run `docker-compose up -d` to launch Airflow and Postgres.
4. <img width="384" height="376" alt="Screenshot 2023-06-01 235918" src="https://github.com/user-attachments/assets/1a10989e-865c-4bac-aa44-6e66d33443c8" />
