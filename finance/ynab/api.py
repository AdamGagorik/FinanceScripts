"""
A wrapper around the YNAB API.
"""
import dataclasses
import typing
import os


from finance.api import BaseHandler, BaseConfig


import ynab_api as ynab


@dataclasses.dataclass()
class YNABConfig(BaseConfig):
    """
    The configuration for YNAB.
    """
    @property
    def ynab_apikey(self) -> str:
        """
        Get the token for the YNAB REST API.
        """
        return os.environ.get('YNAB_APIKEY', '')


class YNABHandler(BaseHandler):
    """
    A wrapper around the YNAB API.
    """
    def __init__(self, config: YNABConfig = None):
        super().__init__(config=config if config is not None else YNABConfig())
        self._api_config: typing.Union[ynab.Configuration, None] = None
        self._api_client: typing.Union[ynab.ApiClient, None] = None
        self._api_object: dict = {}

    @property
    def client(self) -> ynab.ApiClient:
        """
        Log into YNAB and save the session.
        """
        if self._api_config is None:
            self._api_config: ynab.Configuration = ynab.Configuration()
            self._api_config.api_key_prefix['Authorization'] = 'Bearer'
            self._api_config.api_key['Authorization'] = self.config.ynab_apikey

        if self._api_client is None:
            self._api_client: ynab.ApiClient = ynab.ApiClient(self._api_config)
            return self._api_client
        else:
            return self._api_client

    def _get_api_object(self, key: str, klass: typing.Callable):
        """
        Fetch the API object or create and store it.
        """
        try:
            return self._api_object[key]
        except KeyError:
            self._api_object[key] = klass(self.client)
            return self._api_object[key]

    @property
    def budgets(self) -> ynab.BudgetsApi:
        """Create or get existing API instance"""
        return self._get_api_object('budgets', ynab.BudgetsApi)

    @property
    def accounts(self) -> ynab.AccountsApi:
        """Create or get existing API instance"""
        return self._get_api_object('accounts', ynab.AccountsApi)

    @property
    def transactions(self) -> ynab.TransactionsApi:
        """Create or get existing API instance"""
        return self._get_api_object('transactions', ynab.TransactionsApi)
