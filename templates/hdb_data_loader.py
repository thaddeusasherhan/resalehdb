##Source: https://data.gov.sg/datasets/d_8b84c4ee58e3cfc0ece0d773c8ca6abc/view
DATASET_ID = 'd_8b84c4ee58e3cfc0ece0d773c8ca6abc'

## Dataset and Column Metadata
import json
import requests
import time
import pandas as pd

class HDBDataLoader:
    def __init__(self, dataset_id):
        self.s = requests.Session()
        self.s.headers.update({'referer': 'https://colab.research.google.com'})
        self.base_url = "https://api-production.data.gov.sg"
        self.DATASET_ID = dataset_id

    def get_metadata(self):
        """Fetch and return dataset metadata"""
        url = self.base_url + f"/v2/public/api/datasets/{self.DATASET_ID}/metadata"
        response = self.s.get(url)
        data = response.json()['data']
        column_metadata = data.pop('columnMetadata', None)
        return data, column_metadata

    def download_file(self):
        """Download the dataset file and return as DataFrame"""
        # initiate download
        initiate_url = f"https://api-open.data.gov.sg/v1/public/api/datasets/{self.DATASET_ID}/initiate-download"
        initiate_response = self.s.get(
            initiate_url,
            headers={"Content-Type": "application/json"},
            json={}
        )
        print(initiate_response.json()['data']['message'])

        # poll download
        MAX_POLLS = 5
        for i in range(MAX_POLLS):
            poll_url = f"https://api-open.data.gov.sg/v1/public/api/datasets/{self.DATASET_ID}/poll-download"
            poll_response = self.s.get(
                poll_url,
                headers={"Content-Type": "application/json"},
                json={}
            )
            
            if "url" in poll_response.json()['data']:
                download_url = poll_response.json()['data']['url']
                df = pd.read_csv(download_url)
                print("\nDataframe loaded!")
                return df
            
            if i == MAX_POLLS - 1:
                print(f"{i+1}/{MAX_POLLS}: No result found, possible error with dataset")
            else:
                print(f"{i+1}/{MAX_POLLS}: No result yet, continuing to poll")
            time.sleep(3)
        
        raise Exception("Failed to download file after multiple attempts")

def filter_by_date(df, start_date='2021-01-01', end_date='2025-04-30'):
    """Filter DataFrame by date range"""
    df['month'] = pd.to_datetime(df['month'], format='%Y-%m')
    return df[(df['month'] >= start_date) & (df['month'] <= end_date)]