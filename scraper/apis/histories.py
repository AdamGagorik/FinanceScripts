"""
Handle the API to fetch history data.
"""
import dataclasses
import calendar
import datetime
import requests
import logging


import scraper.base


@dataclasses.dataclass()
class History(scraper.base.ObjectMapping):
    """
    An object with history data.
    """
    accountName: str = ''
    userAccountId: int = -1
    dateRangeBalanceValueChange: float = 0.0
    dateRangePerformanceValueChange: float = 0.0
    cashFlow: float = 0.0
    expense: float = 0.0
    income: float = 0.0
    percentOfTotal: float = 0.0
    t0: datetime.datetime = datetime.datetime(1900, 1, 1)
    t1: datetime.datetime = datetime.datetime(1900, 1, 1)
    dt: int = 0


class HistoriesScraper(scraper.base.Scraper):
    """
    Scrape the historiess data from personal capital.
    """
    __reload_yaml__: str = '{self.t0:%Y-%m-%d}-{self.dt:03d}-histories.yaml'
    __fillna_yaml__: str = 'fillna-histories.yaml'
    __store_class__: type = History

    def __init__(self, *args, t0: datetime.datetime, dt: int, **kwargs):
        """
        Parameters:
            t0: The start time to fetch histories.
            dt: The number of days after the start time.
        """
        self.dt: int = dt
        self.t0: datetime.datetime = t0
        self.t1: datetime.datetime = t0 + datetime.timedelta(days=dt)
        super().__init__(*args, **kwargs)
        logging.debug('t0: %s', self.t0)
        logging.debug('t1: %s', self.t1)

    def fetch(self) -> list:
        """
        The logic of the API call.

        Returns:
            The json dictionary.
        """
        payload: dict = {
            'startDate': self.t0.strftime('%Y-%m-%d'), 'endDate': self.t1.strftime('%Y-%m-%d'),
        }
        data: requests.Response = self.handler.pc.fetch('/account/getHistories', data=payload)

        data: dict = data.json()
        data: list = data.get('spData', {}).get('accountSummaries', [])

        return data


def for_each_month_in(year: int, force: bool = False):
    """
    Fetch the histories given year.

    Parameters:
        year: The year to fetch the histories for.
        force: Use the API even if the store exists?
    """
    for month in range(1, 13):
        weekday, numdays = calendar.monthrange(year, month)
        kwargs = dict(t0=datetime.datetime(year, month, 1), dt=numdays - 1)
        yield HistoriesScraper.export(**kwargs, stub='{t0:%Y-%m-%d}-{dt:03d}-histories.csv', force=force)
