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
    def __init__(self, handler: scraper.handler.PCHandler):
        """
        Parameters:
            handler: The personal capital api handler instance.
        """
        super().__init__(handler, 'transactions')

    def fetch(self, t0: datetime.datetime = None, dt: datetime.timedelta = None) -> dict:
        """
        The logic of the API call.

        Returns:
            The json dictionary.
        """
        if t0 is None:
            t0: datetime.datetime = self.handler.config.dt

        t0: datetime.datetime = t0.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=datetime.timezone.utc)

        if dt is None:
            dt: datetime.timedelta = datetime.timedelta(days=1)

        t1: datetime.datetime = t0 + dt

        t0: str = t0.strftime('%Y-%m-%d')
        t1: str = t1.strftime('%Y-%m-%d')

        payload: dict = {
            'startDate': t0, 'endDate': t1, 'page': 0, 'rows_per_page': 100,
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
