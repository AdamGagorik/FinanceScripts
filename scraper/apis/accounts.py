"""
Handle the API to fetch account data.
"""
import dataclasses
import functools
import typing


import scraper.handler
import scraper.base


@dataclasses.dataclass()
class Account(scraper.base.ObjectMapping):
    """
    An object with account data.
    """
    userAccountId: str = ''


class AccountsScraper(scraper.base.Scraper):
    """
    Scrape the accounts data from personal capital.
    """
    def __init__(self, handler: scraper.handler.PCHandler):
        """
        Parameters:
            handler: The personal capital api handler instance.
        """
        super().__init__(handler, 'accounts')

    def fetch(self) -> dict:
        """
        The logic of the API call.

        Returns:
            The json dictionary.
        """
        data: dict = self.handler.pc.fetch('/newaccount/getAccounts2').json()
        data: dict = data.get('spData', {}).get('accounts', [])
        return data

    @property
    @functools.lru_cache(maxsize=1)
    def objects(self) -> typing.List[Account]:
        """
        Get the Account object instances.

        Returns:
            A list of account objects.
        """
        return [Account.safe_init(**account) for account in self.data]
