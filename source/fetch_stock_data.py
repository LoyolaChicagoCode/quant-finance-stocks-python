import requests
import argparse
import csv
import datetime

def fetch_alpha_vantage(api_key, symbol, start_year, end_year):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}&apikey={api_key}&outputsize=full"
    response = requests.get(url)
    data = response.json()["Time Series (Daily)"]
    return {date: values for date, values in data.items() if start_year <= date[:4] <= end_year}

def fetch_iex_cloud(api_key, symbol, start_year, end_year):
    url = f"https://cloud.iexapis.com/stable/stock/{symbol}/chart/max?token={api_key}"
    response = requests.get(url)
    return [item for item in response.json() if start_year <= item["date"][:4] <= end_year]

def fetch_quandl(api_key, symbol, start_year, end_year):
    url = f"https://www.quandl.com/api/v3/datasets/WIKI/{symbol}.json?start_date={start_year}-01-01&end_date={end_year}-12-31&api_key={api_key}"
    response = requests.get(url)
    return response.json()["dataset"]["data"]

def save_to_csv(data, output_file, service):
    with open(output_file, 'w', newline='') as file:
        writer = csv.writer(file)
        if service == 'AlphaVantage':
            for date, daily_data in data.items():
                writer.writerow([date, daily_data['4. close']])
        elif service == 'IEXCloud':
            for daily_data in data:
                writer.writerow([daily_data['date'], daily_data['close']])
        elif service == 'Quandl':
            for entry in data:
                writer.writerow([entry[0], entry[4]])  # date and close price

def main():
    parser = argparse.ArgumentParser(description='Fetch stock data')
    parser.add_argument('--key', required=True, help='API key')
    parser.add_argument('--symbol', required=True, help='Stock symbol')
    parser.add_argument('--service', required=True, choices=['AlphaVantage', 'IEXCloud', 'Quandl'], help='Stock data service')
    parser.add_argument('--start', required=True, help='Start year (YYYY)')
    parser.add_argument('--end', required=True, help='End year (YYYY)')
    parser.add_argument('--output', required=True, help='Output CSV file')
    args = parser.parse_args()

    if args.service == 'AlphaVantage':
        data = fetch_alpha_vantage(args.key, args.symbol, args.start, args.end)
    elif args.service == 'IEXCloud':
        data = fetch_iex_cloud(args.key, args.symbol, args.start, args.end)
    elif args.service == 'Quandl':
        data = fetch_quandl(args.key, args.symbol, args.start, args.end)

    save_to_csv(data, args.output, args.service)
    print(f"Data saved to {args.output}")

if __name__ == "__main__":
    main()

