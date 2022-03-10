import os
import requests
import logging
import json

from config import *


def get_yahoo_configs():
    """Get the Yahoo Finance API configs from the secrets file.
    If the secrets file is invalid or does not exist, it calls
    `create_secrets_file()` to create/overwrite it.
    Returns:
        {dict} -- Yahoo Finance API endpoint and key.
    """

    if os.path.exists(SECRETS_FILE):
        f = open(SECRETS_FILE, 'r')
        try:
            data = json.load(f)
        except Exception as e:
            logging.error(type(e).__name__)
            logging.error("Secrets file {} is invalid.".format(SECRETS_FILE))
            raise
        f.close()
        return data['yahoo']
    else:
        logging.error("[ERROR] File {} does not exist.".format(SECRETS_FILE))
        return None


class YahooFetcher():
    def __init__(self):
        self.configs = get_yahoo_configs()
        self.raw_data = None
        self.clean_data = None

    def fetch_all(self):
        response = requests.get(
            self.configs['endpoint'],
            params={
                'symbols': YAHOO_STOCKS,
                'region': 'US',
                'lang': 'en',
            },
            headers={
                'Accept': 'application/json',
                # 'X-API-KEY': self.configs['key']
            }
        )

        status = response.status_code
        if status != 200:
            raise Exception(
                f"[FAIL] Yahoo fetch all returned status code {status}"
            )

        self.raw_data = response.json()

    def raw_to_clean(self):
        self.clean_data = []

        tickers = self.raw_data['quoteResponse']['result']
        for t in tickers:
            stock = {
                'name': t['shortName'],
                'symbol': t['symbol'],
                'price': float(t['ask']),
            }
            self.clean_data.append(stock)

    def run(self):
        self.fetch_all()
        self.raw_to_clean()
