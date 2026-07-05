import requests
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import pandas as pd

class XMIngestor:
    def __init__(self, base_url="http://api.xm.com.co/api/lists"):
        self.base_url = base_url
        self.session = requests.Session()

    def get_data(self, variable_name, start_date, end_date):
        url = f"{self.base_url}"
        payload = {
            "MetricId": variable_name,
            "StartDate": start_date.strftime("%Y-%m-%d"),
            "EndDate": end_date.strftime("%Y-%m-%d")
        }
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    def process_daily_entities(self, entities):
        data = []
        for entity in entities:
            for daily_entity in entity['DailyEntities']:
                row = {
                    'timestamp': pd.to_datetime(daily_entity['Timestamp']),
                    'value': daily_entity['Value']
                }
                data.append(row)
        return pd.DataFrame(data)

    def process_hourly_entities(self, entities):
        data = []
        for entity in entities:
            for hourly_entity in entity['HourlyEntities']:
                row = {
                    'timestamp': pd.to_datetime(hourly_entity['Timestamp']),
                    'value': hourly_entity['Value']
                }
                data.append(row)
        return pd.DataFrame(data)

    def fetch_variable_data(self, variable_name, start_date, end_date):
        json_response = self.get_data(variable_name, start_date, end_date)
        if variable_name in ['AportesHidricos', 'NivelEmbalsesVolumeUtil', 'PrecEsca']:
            df = self.process_daily_entities(json_response['Entities'])
        else:
            df = self.process_hourly_entities(json_response['Entities'])
        return df

    def fetch_data_for_period(self, start_date, end_date):
        variables = [
            "AportesHidricos",
            "NivelEmbalsesVolumeUtil",
            "PrecOferDesp",
            "PrecEsca"
        ]
        dataframes = {var: [] for var in variables}
        for variable in variables:
            print(f"Fetching {variable} from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
            df = self.fetch_variable_data(variable, start_date, end_date)
            dataframes[variable].append(df)
        return dataframes

    def save_to_parquet(self, dataframes):
        for variable, dfs in dataframes.items():
            combined_df = pd.concat(dfs, ignore_index=True)
            file_path = f"../data/{variable.lower()}_historical.parquet"
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            combined_df.to_parquet(file_path, index=False)
            print(f"Data saved to {file_path}")

def main():
    start_date = datetime(2010, 1, 1)
    end_date = datetime(2026, 6, 30)
    current_date = start_date

    ingestor = XMIngestor()
    all_dataframes = {var: [] for var in ["AportesHidricos", "NivelEmbalsesVolumeUtil", "PrecOferDesp", "PrecEsca"]}

    while current_date <= end_date:
        next_month = (current_date + relativedelta(months=1)).replace(day=1) - timedelta(days=1)
        dataframes = ingestor.fetch_data_for_period(current_date, next_month)
        for variable, df in dataframes.items():
            all_dataframes[variable].append(df)
        current_date = next_month + timedelta(days=1)

    ingestor.save_to_parquet(all_dataframes)

if __name__ == "__main__":
    main()
