from argparse import ArgumentParser
import requests
from prometheus_client import start_http_server, CollectorRegistry, generate_latest, Gauge
import json
import schedule
import time

VERSION = 0.1
newrelic_synthetics_up = Gauge('newrelic_synthetics_up', 
                               'Success/failure of a New Relic Synthetic check',
                               [ 'monitor_id', 'monitor_name',
                                 'location', 'location_name',
                                 'account' ])

def setup_and_parse_command_line():
    parser = ArgumentParser(description='Generate metrics for New Relic Synthetics results')
    parser.add_argument('--port', type=int, default=9234,
                        help='Port for /metrics endpoint')
    parser.add_argument('--account', required=True, help='New Relic account number')
    parser.add_argument('--query_key', required=True, help='Query key used to query NR Insights')
    parser.add_argument('--interval_minutes', type=int, default=1, 
                        help='Interval, in minutes, for running scans')
    parser.add_argument('--version', action='store_true',
                        help='Print version and exit')
    return parser.parse_args()

def generate_metrics_from_json(results, account):
    monitor_ts = {}
    
    for result in results['results']:
        for event in result['events']:
            if not event['monitorId'] in monitor_ts.keys():
                monitor_ts[event['monitorId']] = event['timestamp']
            if event['timestamp'] >= monitor_ts[event['monitorId']]:
                up = 1 if event['result'] == 'SUCCESS' else 0
                newrelic_synthetics_up.labels(event['monitorId'], event['monitorName'],
                                              event['location'], event['locationLabel'],
                                              account).set(up)
                

def fetch_synthetics(url, headers, account):
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        generate_metrics_from_json(r.json(), account)

def serve(args):
    if args.version:
        print(VERSION)
    url = "https://insights-api.newrelic.com/v1/accounts/{0}/query?nrql=SELECT+%2A+FROM+SyntheticCheck+SINCE+30+MINUTES+AGO".format(args.account)
    headers = {
        "Accept": "application/json",
        "X-Query-Key": args.query_key
    }

    fetch_synthetics(url, headers, args.account)
    start_http_server(args.port)
    schedule.every(args.interval_minutes).minutes.do(fetch_synthetics, 
                                                     url, headers, args.account)
    while True:
        schedule.run_pending()
        time.sleep(10)

if __name__ == "__main__":
    serve(setup_and_parse_command_line())
