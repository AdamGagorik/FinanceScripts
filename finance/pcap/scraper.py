import typing


from finance.pcap.api import PCAPHandler
from finance.objmap import ObjectMapping
from finance.scraper import BaseScraper


class PCAPScraper(BaseScraper):
    """
    A base class that can preform API calls or reload data using a PCAP handler.
    """
    __reload_yaml__: str = '{dt:%Y-%m-%d}-finance.yaml'
    __fillna_yaml__: str = 'fillna-finance.yaml'
    __api_handler__: typing.Callable = PCAPHandler
    __store_class__: ObjectMapping = ObjectMapping

    def fetch(self) -> list:
        """
        The logic of the API call.
        """
        raise NotImplementedError

    @property
    def handler(self) -> PCAPHandler:
        """
        Get the handler instance.
        """
        return self._handler
