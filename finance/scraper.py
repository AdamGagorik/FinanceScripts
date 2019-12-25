"""
Download and cache files from a REST API.
"""
import pandas as pd
import dataclasses
import functools
import logging
import typing
import yaml
import os


from finance.api import BaseHandler
from finance.objmap import ObjectMapping


class BaseScraper:
    """
    Download and cache files from a REST API.
    """
    __reload_yaml__: str = '{dt:%Y-%m-%d}-finance.yaml'
    __fillna_yaml__: str = 'fillna-finance.yaml'
    __api_handler__: typing.Callable = BaseHandler
    __store_class__: ObjectMapping = ObjectMapping

    def __init__(self, handler=None, force: bool = False):
        """
        Parameters:
            handler: The api handler instance.
            force: Use the API even if the store exists?
        """
        #: The personal capital api handler
        handler = handler if handler is not None else self.__api_handler__(config=None)
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
        instance = cls(handler=cls.__api_handler__(config=None), **kwargs)
        instance.frame.to_csv(stub.format(**kwargs, config=instance.handler.config), index=False)
        if debug:
            logging.debug('%s\n%s', cls.__name__, instance.frame)
            return instance
        else:
            return instance
