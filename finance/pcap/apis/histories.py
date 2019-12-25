"""
Handle the API to fetch history data.
"""
import pandas as pd
import dataclasses
import calendar
import datetime
import requests
import logging
import typing


import finance.base


@dataclasses.dataclass()
class History(finance.base.ObjectMapping):
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


class HistoriesScraper(finance.base.PCAPScraper):
    """
    Scrape the historiess data from personal capital.
    """
    __reload_yaml__: str = '{self.t0:%Y-%m-%d}-{self.dt:03d}-pcap-histories.yaml'
    __fillna_yaml__: str = 'fillna-pcap-histories.yaml'
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


def for_each_week_in(stub: str, year: int, month: int = 1, **kwargs) -> typing.Generator[pd.DataFrame, None, None]:
    """
    Fetch the histories for each week in the given year.

    Parameters:
        stub: The name of the CSV file to save.
        year: The year to fetch the histories for.
        month: The month to start the iteration in.
    """
    ti = datetime.datetime(year, month, 1)
    tf = min(datetime.datetime.today(), datetime.datetime(year, 12, 31))
    for t1 in pd.date_range(start=ti, end=tf, freq='W-SAT'):
        t0 = t1 - datetime.timedelta(days=6)
        t0 = t0 if t0 >= ti else ti
        _kwargs = dict(t0=t0, dt=(t1 - t0).days, **kwargs)
        logging.debug('fetching %s to %s : %s', t0, t1, t1 - t0)
        yield HistoriesScraper.export(**_kwargs, stub=stub, debug=False).frame


def for_each_month_in(stub: str, year: int, **kwargs) -> typing.Generator[pd.DataFrame, None, None]:
    """
    Fetch the histories for each month in the given year.

    Parameters:
        stub: The name of the CSV file to save.
        year: The year to fetch the histories for.
    """
    for month in range(1, 13):
        weekday, numdays = calendar.monthrange(year, month)
        t0 = datetime.datetime(year, month, 1)
        t1 = t0 + datetime.timedelta(days=numdays)
        _kwargs = dict(t0=t0, dt=numdays - 1, **kwargs)
        logging.debug('fetching %s to %s : %s', t0, t1, t1 - t0)
        yield HistoriesScraper.export(**_kwargs, stub=stub, debug=False).frame


def frame_for_each_week_in(**kwargs) -> pd.DataFrame:
    """
    Fetch the histories for each week in the given year.
    """
    return pd.concat(finance.pcap.apis.histories.for_each_week_in(**kwargs), ignore_index=True)


def frame_for_each_month_in(**kwargs) -> pd.DataFrame:
    """
    Fetch the histories for each month in the given year.
    """
    return pd.concat(finance.pcap.apis.histories.for_each_month_in(**kwargs), ignore_index=True)
