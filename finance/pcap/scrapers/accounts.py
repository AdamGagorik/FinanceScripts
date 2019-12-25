"""
Handle the API to fetch account data.
"""
import dataclasses
import requests


import finance.scraper
import finance.objmap
import finance.pcap.api
import finance.pcap.scraper


@dataclasses.dataclass()
class Account(finance.objmap.ObjectMapping):
    """
    An object with account data.
    """
    userAccountId: str = ''


class AccountsScraper(finance.pcap.scraper.PCAPScraper):
    """
    Scrape the accounts data from personal capital.
    """
    __reload_yaml__: str = '{dt:%Y-%m-%d}-pcap-accounts.yaml'
    __fillna_yaml__: str = 'fillna-pcap-accounts.yaml'
    __store_class__: type = Account

    def fetch(self) -> list:
        """
        The logic of the API call.

        Returns:
            The json dictionary.
        """
        payload: dict = {}
        data: requests.Response = self.handler.client.fetch('/newaccount/getAccounts2', data=payload)

        data: dict = data.json()
        data: list = data.get('spData', {}).get('accounts', [])

        return data
