"""
A script to download the market value for an account.
The script is given a starting date and a time period freqency.
The rows of the resulting dataframe will display the market value at the timestamps.
"""
import pandas as pd
import calendar
import argparse
import datetime
import logging


import scraper.apis
import scraper.helpers


from scraper.helpers import yyyy_mm_dd


def make_frame(samples: pd.Series):
    """
    Given the endpoints of a date range, create an a dataframe of intervals [t0, t1, dt].
    """
    frame = pd.DataFrame({
        't0': samples[:-1],
        't1': samples[+1:],
    })

    frame['dt'] = (frame['t1'] - frame['t0']).dt.days
    return frame


def days_of_month(year: int, month: int) -> pd.DataFrame:
    """
    Create a dataframe with samples [t0, t1, dt] for each day in a given month, of a given year.
    """
    weekday, periods = calendar.monthrange(year, month)
    start = datetime.datetime(year, month, 1, tzinfo=datetime.timezone.utc)

    samples = pd.date_range(start=start, periods=periods + 1, freq='D', normalize=False, tz=datetime.timezone.utc)
    samples = samples - datetime.timedelta(microseconds=1)

    return make_frame(samples)


def weeks_of_month(year: int, month: int) -> pd.DataFrame:
    """
    Create a dataframe with samples [t0, t1, dt] for each week in a given month, of a given year.
    """
    start = datetime.datetime(year, 1, 1, tzinfo=datetime.timezone.utc) - datetime.timedelta(days=6)

    samples = pd.date_range(start=start, periods=53, freq='W-MON', normalize=False, tz=datetime.timezone.utc)
    samples = samples - datetime.timedelta(microseconds=1)

    return make_frame(samples)


def months_of_year(year: int) -> pd.DataFrame:
    """
    Create a dataframe with samples [t0, t1, dt] for month in a given year.
    """
    start = datetime.datetime(year, 1, 1, tzinfo=datetime.timezone.utc)

    samples = pd.date_range(start=start, periods=13, freq='MS', normalize=False, tz=datetime.timezone.utc)
    samples = samples - datetime.timedelta(microseconds=1)

    return make_frame(samples)


# noinspection DuplicatedCode
def get_arguments() -> argparse.Namespace:
    """
    Get the command line arguments.
    """
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)

    start = datetime.datetime.now(tz=datetime.timezone.utc)
    parser.add_argument('--force', action='store_true', help='force redownload?')
    parser.add_argument('--start', default=start, type=yyyy_mm_dd, help='The starting YYYY/MM/DD of the sample')
    parser.add_argument('--frequency', default='W', type=str, choices=['D', 'W', 'M'], help='The sampling frequency')

    return parser.parse_args()


def main(force: bool, start: datetime.datetime, frequency: str):
    """
    A script to download the market value for an account.
    """
    frame: pd.DataFrame = {
        'D': lambda: days_of_month(start.year, start.month),
        'W': lambda: weeks_of_month(start.year, start.month),
        'M': lambda: months_of_year(start.year),
    }[frequency]()

    logging.debug('\n%s', frame)


if __name__ == '__main__':
    scraper.helpers.run(main, get_arguments)
