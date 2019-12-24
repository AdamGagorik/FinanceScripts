"""
A script to play with the personal capital api.
"""
import pandas as pd
import dataclasses
import functools
import logging
import inspect
import typing
import yaml
import os


from scraper.handler import BaseHandler
from scraper.handler import YNABHandler
from scraper.handler import PCAPHandler


# noinspection PyArgumentList
@dataclasses.dataclass()
class ObjectMapping:
    """
    A base class to aid in creating objects from JSON.
    """
    @classmethod
    def safe_init(cls, instance: typing.Any, **kwargs) -> 'ObjectMapping':
        """
        Create an object from the keyword arguments.
        Silently ignore any keyword arguments that are not known.
        """
        skwargs = {}
        for name in inspect.signature(cls).parameters:
            try:
                skwargs[name] = kwargs[name]
            except KeyError:
                try:
                    skwargs[name] = getattr(instance, name)
                except AttributeError:
                    pass

        return cls(**skwargs)

    def fillna(self, rules: typing.List[typing.MutableMapping]) -> 'ObjectMapping':
        """
        Fill in missing values based on the list of rules.

        The rules is a list of of `where` and `value` mappings.
        An update occurs when all instance variables match the `where` items.
        The items from the `values` mapping are used when the update step occurs.

        Parameters:
            rules: A list of rule mappings.

        Returns:
            The updated instance with missing values filled in based on the rules.
        """
        for i, rule in enumerate(rules):
            if self._matches(**rule['where']):
                self._update(**rule['value'])
                rules.pop(i)
                break

        return self

    def _matches(self, **kwargs) -> bool:
        """
        Check to see if key-value pair matches.

        Returns:
            True if all items match.
        """
        if not kwargs:
            return False

        for k, v in kwargs.items():
            if getattr(self, k) != v:
                return False

        return True

    def _update(self, **kwargs):
        """
        Update attributes using key-value pairs.
        """
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)
            else:
                raise AttributeError(k)


class BaseScraper:
    """
    A base class that can preform API calls or reload data using a handler.
    """
    __reload_yaml__: str = '{dt:%Y-%m-%d}-scraper.yaml'
    __fillna_yaml__: str = 'fillna-scraper.yaml'
    __api_handler__: typing.Callable = BaseHandler
    __store_class__: ObjectMapping = ObjectMapping

    def __init__(self, handler=None, force: bool = False):
        """
        Parameters:
            handler: The api handler instance.
            force: Use the API even if the store exists?
        """
        #: The personal capital api handler
        handler = handler if handler is not None else self.__api_handler__()
        self._handler = handler
        #: The name of the file to store the API results in
        self.store: str = os.path.join(handler.config.workdir, self.__reload_yaml__)
        self.store: str = self.store.format(dt=handler.config.dt, self=self)
        #: The data that was fetched as json from the API call
        self._data: typing.Union[list, None] = None
        self.force: bool = force

    @property
    def handler(self) -> BaseHandler:
        """
        Get the handler instance.
        """
        return self._handler

    @property
    def data(self) -> list:
        """
        Get the list of JSON objects data.
        """
        if self._data is None:
            self.reload()

        return self._data

    def fetch(self) -> list:
        """
        The logic of the API call.
        """
        raise NotImplementedError

    def reload(self) -> 'BaseScraper':
        """
        Download the data from the API or reload it from disk.
        """
        if self.force or not os.path.exists(self.store):
            self._data = self.fetch()
            with open(self.store, 'w') as stream:
                yaml.dump(self.data, stream)
        else:
            with open(self.store, 'r') as stream:
                self._data = yaml.load(stream, yaml.SafeLoader)

        return self

    @property
    @functools.lru_cache(maxsize=1)
    def rules(self):
        """
        Get the list of fillna rules from the yaml file.
        """
        path: str = os.path.join(self.handler.config.workdir, self.__fillna_yaml__)
        if os.path.exists(path):
            return yaml.load(open(path, 'r'), yaml.SafeLoader).get('rules', [])
        else:
            return []

    @property
    @functools.lru_cache(maxsize=1)
    def objects(self) -> list:
        """
        Get the store object instances.

        Returns:
            A list of objects.
        """
        return [self.__store_class__.safe_init(instance=self, **obj).fillna(self.rules) for obj in self.data]

    def __iter__(self) -> typing.Generator[ObjectMapping, None, None]:
        """
        Iterate over the JSON objects.

        Yields:
            The JSON objects.
        """
        for instance in self.objects:
            yield instance

    @property
    @functools.lru_cache(maxsize=1)
    def frame(self) -> pd.DataFrame:
        """
        Get the objects as a dataframe.

        Returns:
            The dataframe.
        """
        frame_: pd.DataFrame = pd.DataFrame(dataclasses.asdict(obj) for obj in self.objects)

        columns: list = [f.name for f in dataclasses.fields(self.__store_class__) if f.name in frame_.columns]
        if columns:
            frame_: pd.DataFrame = frame_.sort_values(by=columns)
            frame_: pd.DataFrame = frame_.reset_index(drop=True)

        return frame_

    @classmethod
    def export(cls, stub: str, debug: bool = True, **kwargs) -> 'BaseScraper':
        """
        Create and instance and save the resulting dataframe to a file.

        Parameters:
            stub: The name of the CSV file to save.
            debug: Log the dataframe to the screen?
            **kwargs: The key word arguments to the constructor.
        """
        instance = cls(handler=cls.__api_handler__(), **kwargs)
        instance.frame.to_csv(stub.format(**kwargs, config=instance.handler.config), index=False)
        if debug:
            logging.debug('%s\n%s', cls.__name__, instance.frame)
            return instance
        else:
            return instance


class PCAPScraper(BaseScraper):
    """
    A base class that can preform API calls or reload data using a PCAP handler.
    """
    __reload_yaml__: str = '{dt:%Y-%m-%d}-scraper.yaml'
    __fillna_yaml__: str = 'fillna-scraper.yaml'
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


class YNABScraper(BaseScraper):
    """
    A base class that can preform API calls or reload data using a YNAB handler.
    """
    __reload_yaml__: str = '{dt:%Y-%m-%d}-scraper.yaml'
    __fillna_yaml__: str = 'fillna-scraper.yaml'
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
