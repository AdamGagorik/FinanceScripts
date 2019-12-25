"""
Handle the API to fetch account data.
"""
import dataclasses
import requests


import finance.base


@dataclasses.dataclass()
class Holding(finance.base.ObjectMapping):
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


class HoldingsScraper(finance.base.PCAPScraper):
    """
    Scrape the holdings data from personal capital.
    """
    __reload_yaml__: str = '{dt:%Y-%m-%d}-pcap-holdings.yaml'
    __fillna_yaml__: str = 'fillna-pcap-holdings.yaml'
    __store_class__: type = Holding

    def fetch(self) -> list:
        """
        The logic of the API call.

        Returns:
            THe json dictionary.
        """
        payload: dict = {}
        data: requests.Response = self.handler.pc.fetch('/invest/getHoldings', data=payload)

        data: dict = data.json()
        data: list = data.get('spData', {}).get('holdings', [])

        return data
