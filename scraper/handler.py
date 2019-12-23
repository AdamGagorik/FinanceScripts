"""
A wrapper around the personal capital API from the personalcapital module.
"""
import functools
import typing
import json


from personalcapital import TwoFactorVerificationModeEnum
from personalcapital import RequireTwoFactorException
from personalcapital import PersonalCapital


import ynab_api as ynab


from scraper.config import BaseConfig
from scraper.config import YNABConfig
from scraper.config import PCAPConfig


class BaseHandler:
    """
    Handler to create a REST session.
    """
    __config_class__ = BaseConfig

    def __init__(self, config=None):
        #: The scraper config instance
        self.config = config if config is not None else self.__config_class__()


class YNABHandler(BaseHandler):
    """
    Handler to create the Personal Capital session.
    """
    __config_class__ = YNABConfig

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._api_client: typing.Union[ynab.ApiClient, None] = None
        self._api_config: typing.Union[ynab.Configuration, None] = None
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


class PCAPHandler(BaseHandler):
    """
    Handler to create the Personal Capital session.
    """
    __config_class__ = PCAPConfig

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #: The personal capital instance
        self._pc: typing.Union[PersonalCapital, None] = None

    @property
    def pc(self) -> PersonalCapital:
        """
        Log into personal capital and save the session.
        """
        if self._pc is None:
            self._pc: PersonalCapital = PersonalCapital()

            if self.cookies:
                self._pc.set_session(self.cookies)

            try:
                self._pc.login(self.config.username, self.config.password)
            except RequireTwoFactorException:
                self._pc.two_factor_challenge(TwoFactorVerificationModeEnum.SMS)
                self._pc.two_factor_authenticate(TwoFactorVerificationModeEnum.SMS, self.code)
                self._pc.authenticate_password(self.config.password)

            with open(self.config.cookies, 'w') as stream:
                stream.write(json.dumps(self._pc.get_session()))

            return self._pc
        else:
            return self._pc

    @property
    @functools.lru_cache(maxsize=1)
    def code(self) -> str:
        """
        Get the personal capital two factor auth code.
        """
        return input('code: ')

    @property
    @functools.lru_cache(maxsize=1)
    def cookies(self) -> dict:
        """
        Get the session cookies dictionary if it was saved.
        """
        try:
            with open(self.config.cookies, 'r') as stream:
                return json.load(stream)
        except FileNotFoundError:
            return {}
