"""
Handle the API to fetch transaction data.
"""
import dataclasses
import datetime
import requests


import finance.scraper
import finance.objmap
import finance.pcap.api
import finance.pcap.scraper


@dataclasses.dataclass()
class Transaction(finance.objmap.ObjectMapping):
    """
    An object with transaction data.
    """
    accountName: str = ''
    userAccountId: int = -1
    userTransactionId: int = -1
    transactionDate: str = ''
    amount: float = 0.0

    def __post_init__(self):
        self.transactionDate: datetime.datetime = \
            datetime.datetime.strptime(self.transactionDate, '%Y-%m-%d')


class TransactionsScraper(finance.pcap.scraper.PCAPScraper):
    """
    Scrape the transactions data from personal capital.
    """
    __reload_yaml__: str = '{self.t0:%Y-%m-%d}-{self.dt:03d}-pcap-transactions.yaml'
    __fillna_yaml__: str = 'fillna-pcpa-transactions.yaml'
    __store_class__: type = Transaction

    def __init__(self, *args, t0: datetime.datetime, dt: int, **kwargs):
        """
        Parameters:
            t0: The start time to fetch transactions.
            dt: The number of days after the start time.
        """
        self.dt: int = dt
        self.t0: datetime.datetime = t0
        self.t1: datetime.datetime = t0 + datetime.timedelta(days=dt)
        super().__init__(*args, **kwargs)

    def fetch(self) -> list:
        """
        The logic of the API call.

        Returns:
            The json dictionary.
        """
        payload: dict = {
            'startDate': self.t0.strftime('%Y-%m-%d'), 'endDate': self.t1.strftime('%Y-%m-%d'),
            'page': 0, 'rows_per_page': 4096, 'component': 'DATAGRID',
            'sort_cols': 'transactionTime', 'sort_rev': 'true',
        }
        data: requests.Response = self.handler.client.fetch('/transaction/getUserTransactions', data=payload)

        data: dict = data.json()
        data: list = data.get('spData', {}).get('transactions', [])

        return data
