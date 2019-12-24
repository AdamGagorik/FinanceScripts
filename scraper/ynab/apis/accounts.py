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
    id: str = ''
    name: str = ''
    type: str = ''

    # ammounts
    balance: int = 0
    cleared_balance: int = 0
    uncleared_balance: int = 0

    # booleans
    closed: bool = False
    deleted: bool = False
    on_budget: bool = True


class AccountsScraper(scraper.base.YNABScraper):
    """
    Scrape the accounts data from YNAB.
    """
    __reload_yaml__: str = '{dt:%Y-%m-%d}-ynab-accounts.yaml'
    __fillna_yaml__: str = 'fillna-ynab-accounts.yaml'
    __store_class__: type = Account

    def __init__(self, *args, budget_id: str, **kwargs):
        """
        Parameters:
            budget_id: The budget to fetch the accounts for.
        """
        self.budget_id: str = budget_id
        super().__init__(*args, **kwargs)

    def fetch(self) -> list:
        """
        The logic of the API call.

        Returns:
            The json dictionary.
        """
        accounts: ynab.AccountResponse = self.handler.accounts.get_accounts(self.budget_id)

        data: dict = accounts.to_dict().get('data', {})
        data: list = data.get('accounts', [])

        return data
