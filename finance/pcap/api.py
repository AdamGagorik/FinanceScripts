"""
A wrapper around the Personal Capital API.
"""
import dataclasses
import functools
import typing
import json
import os


from finance.api import BaseHandler, BaseConfig


from personalcapital import TwoFactorVerificationModeEnum
from personalcapital import RequireTwoFactorException
from personalcapital import PersonalCapital


@dataclasses.dataclass()
class PCAPConfig(BaseConfig):
    """
    The configuration for Personal Capital.
    """
    #: The path to the personal capital session cookie
    cookies: str = dataclasses.field(init=False, default='session.json')

    @property
    def username(self) -> str:
        """
        Get the personal capital account username.
        """
        return os.environ.get('PC_USERNAME', '')

    @property
    def password(self) -> str:
        """
        Get the personal capital account password.
        """
        return os.environ.get('PC_PASSWORD', '')

    def __post_init__(self):
        super().__post_init__()
        self.cookies = os.path.join(self.workdir, self.cookies)


class PCAPHandler(BaseHandler):
    """
    A wrapper around the Personal Capital API.
    """
    def __init__(self, config: PCAPConfig = None):
        super().__init__(config=config if config is not None else PCAPConfig())
        self._api_client: typing.Union[PersonalCapital, None] = None

    @property
    def client(self) -> PersonalCapital:
        """
        Log into Personal Capital and save the session.
        """
        if self._api_client is None:
            self._api_client: PersonalCapital = PersonalCapital()

            if self._session_cookies:
                self._api_client.set_session(self._session_cookies)

            try:
                self._api_client.login(self.config.username, self.config.password)
            except RequireTwoFactorException:
                self._api_client.two_factor_challenge(TwoFactorVerificationModeEnum.SMS)
                self._api_client.two_factor_authenticate(TwoFactorVerificationModeEnum.SMS, self._auth_code)
                self._api_client.authenticate_password(self.config.password)

            with open(self.config.cookies, 'w') as stream:
                stream.write(json.dumps(self._api_client.get_session()))

            return self._api_client
        else:
            return self._api_client

    @property
    @functools.lru_cache(maxsize=1)
    def _auth_code(self) -> str:
        """
        Get the personal capital two factor auth code.
        """
        return input('code: ')

    @property
    @functools.lru_cache(maxsize=1)
    def _session_cookies(self) -> dict:
        """
        Get the session cookies dictionary if it was saved.
        """
        try:
            with open(self.config.cookies, 'r') as stream:
                return json.load(stream)
        except FileNotFoundError:
            return {}
