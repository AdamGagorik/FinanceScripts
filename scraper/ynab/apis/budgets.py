import ynab_api as ynab
import pandas as pd
import dataclasses


import scraper.base


@dataclasses.dataclass()
class Budget(scraper.base.ObjectMapping):
    id: str = ''
    name: str = ''


class BudgetsScraper(scraper.base.YNABScraper):
    __reload_yaml__: str = '{dt:%Y-%m-%d}-ynab-budgets.yaml'
    __fillna_yaml__: str = 'fillna-ynab-budgets.yaml'
    __store_class__: type = Budget

    def fetch(self) -> list:
        budgets: ynab.BudgetSummaryResponse = self.handler.budgets.get_budgets()
        data: dict = budgets.to_dict().get('data', {})
        data: list = data.get('budgets', [])
        return data


def resolve_budget_id(budget_id: str, parser: BudgetsScraper = None) -> str:
    if budget_id == 'last-used':
        return budget_id

    parser: BudgetsScraper = parser if parser is not None else BudgetsScraper()
    dframe: pd.DataFrame = parser.frame

    if budget_id in dframe['id']:
        return budget_id
    else:
        dframe.set_index('name', inplace=True)
        return dframe.loc[budget_id, 'id']
