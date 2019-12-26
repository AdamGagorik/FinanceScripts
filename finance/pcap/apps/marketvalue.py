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
import typing
import re
import os


import finance.scrapers
import finance.helpers
import finance.apis


from finance.helpers import yyyy_mm_dd


def make_frame(samples: pd.Series) -> pd.DataFrame:
    """
    Given the endpoints of a date range, create an a dataframe of intervals [t0, t1, dt].
    """
    frame = pd.DataFrame({
        't0': samples[:-1],
        't1': samples[+1:],
    })

    # get today at midnight
    nt = datetime.datetime.now(tz=datetime.timezone.utc)
    nt = datetime.datetime(year=nt.year, month=nt.month, day=nt.day, tzinfo=datetime.timezone.utc)
    nt = nt + datetime.timedelta(days=1, microseconds=-1)

    # start time must be in the past
    frame = frame[frame.t0 < nt]

    # end time must be at most today midnight
    subset = frame.loc[frame.t1 > nt, 't1']
    if not subset.empty:
        # only keep the last most interval
        if len(subset) > 1:
            frame = frame.loc[~frame.index.isin(subset.index[1:])]

        # replace the interval upper bound
        frame.loc[subset.index[0], 't1'] = \
            frame.loc[subset.index[0], 't1'].replace(
                year=nt.year, month=nt.month, day=nt.day)

    frame['dt'] = (frame['t1'] - frame['t0']).dt.days

    return frame.reset_index(drop=True)


def days_of_month(year: int, month: int) -> typing.Tuple[str, pd.DataFrame]:
    """
    Create a dataframe with samples [t0, t1, dt] for each day in a given month, of a given year.
    """
    weekday, periods = calendar.monthrange(year, month)
    start = datetime.datetime(year, month, 1, tzinfo=datetime.timezone.utc)

    samples = pd.date_range(start=start, periods=periods + 1, freq='D', normalize=False, tz=datetime.timezone.utc)
    samples = samples - datetime.timedelta(microseconds=1)

    return r'export/{time:%Y-%m-01}-D-{name}.csv', make_frame(samples)


def weeks_of_month(year: int, month: int) -> typing.Tuple[str, pd.DataFrame]:
    """
    Create a dataframe with samples [t0, t1, dt] for each week in a given month, of a given year.
    """
    start = datetime.datetime(year, 1, 1, tzinfo=datetime.timezone.utc) - datetime.timedelta(days=6)

    samples = pd.date_range(start=start, periods=53, freq='W-MON', normalize=False, tz=datetime.timezone.utc)
    samples = samples - datetime.timedelta(microseconds=1)

    samples = make_frame(samples)
    samples = samples[samples['t1'].dt.month == month]

    return r'export/{time:%Y-%m-01}-W-{name}.csv', samples.reset_index(drop=True)


def months_of_year(year: int) -> typing.Tuple[str, pd.DataFrame]:
    """
    Create a dataframe with samples [t0, t1, dt] for month in a given year.
    """
    start = datetime.datetime(year, 1, 1, tzinfo=datetime.timezone.utc)

    samples = pd.date_range(start=start, periods=13, freq='MS', normalize=False, tz=datetime.timezone.utc)
    samples = samples - datetime.timedelta(microseconds=1)

    return r'export/{time:%Y-01-01}-M-{name}.csv', make_frame(samples)


def get_histories(frame: pd.DataFrame, force: bool) -> typing.Generator[pd.DataFrame, None, None]:
    """
    Fetch the histories in the given intervals.
    """
    handler = finance.apis.pcap.PCAPHandler()
    for index, row in frame.iterrows():
        _kwargs = dict(handler=handler, t0=row['t0'], dt=row['dt'], force=force)
        yield finance.scrapers.pcap.HistoriesScraper(**_kwargs).frame


def add_rowsum(frame):
    """
    Add a totals row to the frame.
    """
    rowsum = pd.DataFrame([frame.select_dtypes('number').agg('sum')])
    rowsum.index = ['Total']

    rowsum = pd.concat([frame.reset_index(drop=True), rowsum], sort=False)
    rowsum = rowsum.fillna('')

    return rowsum


def debug_dataframe(name, frame):
    """
    Format the dataframe and debug it to the logger.
    """
    frame = frame.to_string(formatters={'accountName': lambda value: f'{value:>25}'}, float_format='%.2f')
    logging.debug('\n%s\n%s', name, frame)


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
    parser.add_argument('--ynabframe', action='store_true', help='reformace the dataframe for YNAB import CSV files')

    return parser.parse_args()


def main(force: bool, start: datetime.datetime, frequency: str, ynabframe: bool):
    """
    A script to download the market value for an account.
    """
    stub, frame = {
        'D': lambda: days_of_month(start.year, start.month),
        'W': lambda: weeks_of_month(start.year, start.month),
        'M': lambda: months_of_year(start.year),
    }[frequency]()

    logging.debug('\n%s', frame)

    frame = pd.concat(get_histories(frame, force=force), ignore_index=True)
    frame = frame.sort_values(by=['accountName', 't0'])

    for account_name, account_data in frame.groupby(by='accountName'):
        if ynabframe:
            account_data = pd.DataFrame({
                'Date': account_data['t1'], 'Payee': 'Market',
                'Memo': '', 'Amount': account_data['dateRangePerformanceValueChange']
            })

            account_data = account_data.query('abs(Amount) > 0.0')
            if not account_data.empty:
                os.makedirs('export', exist_ok=True)
                export_name = re.sub(r'[ :]+', '', account_name)
                with open(stub.format(time=start, name=export_name), 'w') as stream:
                    account_data.to_csv(stream, index=False)

        account_data = add_rowsum(account_data)
        debug_dataframe(account_name, account_data)


if __name__ == '__main__':
    finance.helpers.run(main, get_arguments)
