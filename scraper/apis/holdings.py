"""
Handle the API to fetch account data.
"""
import pandas as pd
import dataclasses
import functools
import typing
import yaml
import os


import scraper.handler
import scraper.base


from scraper.apis.accounts import Account


@dataclasses.dataclass()
class Holding(scraper.base.ObjectMapping):
    """
    An object with holding data.
    """
    accountName: str = ''
    ticker: str = ''
    cusip: str = ''
    quantity: float = 0.0
    price: float = 1.0
    value: float = 0.0
    userAccountId: int = -1


class HoldingsScraper(scraper.base.Scraper):
    """
    Scrape the holdings data from personal capital.
    """
    def __init__(self, handler: scraper.handler.PCHandler):
        """
        Parameters:
            handler: The personal capital api handler instance.
        """
        super().__init__(handler, 'holdings')

    def fetch(self, accounts: typing.List[Account]) -> dict:
        """
        The logic of the API call.

        Returns:
            THe json dictionary.
        """
        data: dict = {'userAccountIds': [account.userAccountId for account in accounts]}
        data: dict = self.handler.pc.fetch('/invest/getHoldings', data=data).json()
        data: dict = data.get('spData', {}).get('holdings', [])
        return data

    @property
    @functools.lru_cache(maxsize=1)
    def rules(self):
        """
        Get the list of fillna rules from the yaml file.
        """
        path: str = os.path.join(self.handler.config.workdir, 'fillna-holdings.yaml')
        if os.path.exists(path):
            return yaml.load(open(path, 'r'), yaml.SafeLoader).get('rules', [])
        else:
            return []

    @property
    @functools.lru_cache(maxsize=1)
    def objects(self) -> typing.List[Holding]:
        """
        Get the Holding object instances.

        Returns:
            The holding objects.
        """
        return [Holding.safe_init(**account).fillna(self.rules) for account in self.data]

    @property
    @functools.lru_cache(maxsize=1)
    def frame(self) -> pd.DataFrame:
        """
        Get the holding objects as a dataframe.

        Returns:
            The holdings dataframe.
        """
        return pd.DataFrame(dataclasses.asdict(h) for h in self.objects).sort_values(by='accountName')
