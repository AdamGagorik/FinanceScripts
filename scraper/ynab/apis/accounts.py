"""
Handle the API to fetch account data for YNAB.
"""
import ynab_api as ynab
import dataclasses


import scraper.base


@dataclasses.dataclass()
class Account(scraper.base.ObjectMapping):
    """
    An object with account data.
    """
    # header
    uuid: str = ''
    name: str = ''
    type: str = ''

    # ammounts
    balance: int = 0
    cleared: int = 0
    pending: int = 0

    # booleans
    closed    : bool = False
    deleted   : bool = False
    on_budget : bool = True

    # mapping from JSON
    id                : dataclasses.InitVar[str] = ''
    cleared_balance   : dataclasses.InitVar[int] = 0
    uncleared_balance : dataclasses.InitVar[int] = 0

    def __post_init__(self, id: str, cleared_balance: int, uncleared_balance: int):
        """
        Map the JSON keys to object.
        """
        self.uuid   : str = id
        self.cleared: int = cleared_balance
        self.pending: int = uncleared_balance


class AccountsScraper(scraper.base.YNABScraper):
    """
    Scrape the accounts data from YNAB.
    """
    __reload_yaml__: str = '{dt:%Y-%m-%d}-ynab-accounts.yaml'
    __fillna_yaml__: str = 'fillna-ynab-accounts.yaml'
    __store_class__: type = Account

    def fetch(self) -> list:
        """
        The logic of the API call.

        Returns:
            The json dictionary.
        """
        accounts: ynab.AccountResponse = self.handler.accounts.get_accounts('last-used')

        data: dict = accounts.to_dict().get('data', {})
        data: list = data.get('accounts', [])

        return data
