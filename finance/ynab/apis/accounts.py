import ynab_api as ynab
import dataclasses


import finance.base


from .budgets import resolve_budget_id


@dataclasses.dataclass()
class Account(finance.base.ObjectMapping):
    id: str = ''
    name: str = ''
    type: str = ''

    balance: int = 0
    cleared_balance: int = 0
    uncleared_balance: int = 0

    closed: bool = False
    deleted: bool = False
    on_budget: bool = True


class AccountsScraper(finance.base.YNABScraper):
    __reload_yaml__: str = '{dt:%Y-%m-%d}-ynab-accounts-{self.budget_id}.yaml'
    __fillna_yaml__: str = 'ynab-accounts-fillna.yaml'
    __store_class__: type = Account

    def __init__(self, *args, budget_id: str, **kwargs):
        self.budget_id: str = resolve_budget_id(budget_id)
        super().__init__(*args, **kwargs)

    def fetch(self) -> list:
        accounts: ynab.AccountResponse = self.handler.accounts.get_accounts(self.budget_id)
        data: dict = accounts.to_dict().get('data', {})
        data: list = data.get('accounts', [])
        return data
