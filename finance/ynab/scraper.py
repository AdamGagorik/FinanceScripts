import typing

from finance.objmap import ObjectMapping
from finance.scraper import BaseScraper
from finance.ynab.api import YNABHandler


class YNABScraper(BaseScraper):
    """
    A base class that can preform API calls or reload data using a YNAB handler.
    """
    __reload_yaml__: str = '{dt:%Y-%m-%d}-finance.yaml'
    __fillna_yaml__: str = 'fillna-finance.yaml'
    __api_handler__: typing.Callable = YNABHandler
    __store_class__: ObjectMapping = ObjectMapping

    def fetch(self) -> list:
        """
        The logic of the API call.
        """
        raise NotImplementedError

    @property
    def handler(self) -> YNABHandler:
        """
        Get the handler instance.
        """
        return self._handler