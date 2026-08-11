 
import pandas as pd
import os
import datetime as dt
from datetime import timedelta
import yfinance as yf
import boto3
from dotenv import load_dotenv

load_dotenv()   #reads the variables from .env file and palces them in a os enviroment 

def run_market_etl():
    combined_date = []
    end_date = dt.datetime.now()
    is_sat = end_date.weekday() == 5
    is_sun = end_date.weekday() == 6
    if is_sat:
          start_date= end_date - timedelta(hours=48)
    elif is_sun:
          start_date = end_date - timedelta(hours=72)
    else:
        start_date= end_date - timedelta(hours=24) 
    tickers = ['CVE.TO','BTO.TO']  
    for ticker in tickers:
            raw_data = yf.download(ticker,start=start_date,end=end_date,interval='5m')
            raw_data.columns = raw_data.columns.droplevel(1)   #removed entire layer from the multiindex that reepated the stock symbols
            raw_data['extracted_at'] = dt.datetime.now().strftime('%Y-%m-%d %H:%M%S.%f')
            raw_data=raw_data.reset_index() #flattens multiindex dataframe by now having it a single level index
            raw_data['ticker'] = ticker
           
            combined_date.append(raw_data)
    date = dt.datetime.now().strftime('%Y%m%d_%H%M%S')
    df = pd.concat(combined_date,ignore_index=True)
    path='dags/2026'
    os.makedirs(path,exist_ok=True)
    df.to_csv(f'{path}/market_data_{date}.csv',index=False)
    #upload csv to bucket in AWS clound
    s3 = boto3.client('s3')
    s3.upload_file(
          f'{path}/market_data_{date}.csv',
          'toronto-transit-market-data-pipeline',
          f'market_data_{date}.csv'
          )

if __name__ == "__main__":
    run_market_etl()