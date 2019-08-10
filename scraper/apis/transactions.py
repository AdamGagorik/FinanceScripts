"""
Handle the API to fetch transaction data.
"""
import pandas as pd
import dataclasses
import functools
import datetime
import requests
import typing
import yaml
import os


import scraper.handler
import scraper.base


@dataclasses.dataclass()
class Transaction(scraper.base.ObjectMapping):
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


class TransactionsScraper(scraper.base.Scraper):
    """
    Scrape the transactions data from personal capital.
    """
    def __init__(self, handler: scraper.handler.PCHandler, t0: datetime.datetime, dt: int):
        """
        Parameters:
            handler: The personal capital api handler instance.
        """
        self.t0: datetime.datetime = t0
        self.t1: datetime.datetime = t0 + datetime.timedelta(days=dt)
        super().__init__(handler, f'{self.t0:%Y-%m-%d}-{dt:03d}-transactions.yaml')

    def fetch(self) -> dict:
        """
        The logic of the API call.

        Returns:
            The json dictionary.
        """
        t0: str = self.t0.strftime('%Y-%m-%d')
        t1: str = self.t1.strftime('%Y-%m-%d')

        payload: dict = {
            'startDate': t0, 'endDate': t1, 'page': 0, 'rows_per_page': 4096,
            'sort_cols': 'transactionTime', 'sort_rev': 'true',
            'component': 'DATAGRID'
        }
        data: requests.Response = self.handler.pc.fetch('/transaction/getUserTransactions', data=payload)
        data: dict = data.json().get('spData', {}).get('transactions', [])

        return data

    @property
    @functools.lru_cache(maxsize=1)
    def rules(self):
        """
        Get the list of fillna rules from the yaml file.
        """
        path: str = os.path.join(self.handler.config.workdir, 'fillna-transactions.yaml')
        if os.path.exists(path):
            return yaml.load(open(path, 'r'), yaml.SafeLoader).get('rules', [])
        else:
            return []

    @property
    @functools.lru_cache(maxsize=1)
    def objects(self) -> typing.List[Transaction]:
        """
        Get the Transaction object instances.

        Returns:
            A list of transaction objects.
        """
        return [Transaction.safe_init(**transaction).fillna(self.rules) for transaction in self.data]

    @property
    @functools.lru_cache(maxsize=1)
    def frame(self) -> pd.DataFrame:
        """
        Get the transaction objects as a dataframe.

        Returns:
            The transactions dataframe.
        """
        _frame: pd.DataFrame = pd.DataFrame(dataclasses.asdict(t) for t in self.objects)
        _frame: pd.DataFrame = _frame.sort_values(by=['accountName', 'transactionDate'])
        _frame: pd.DataFrame = _frame.reset_index(drop=True)
        return _frame
