"""
A script to save a history CSV for each month in the given year.
"""
import pandas as pd
import argparse
import logging


import finance.apis
import finance.helpers


# noinspection DuplicatedCode
def get_arguments() -> argparse.Namespace:
    """
    Get the command line arguments.
    """
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--force', action='store_true', help='force redownload?')
    parser.add_argument('--stub', default='{t0:%Y-%m-%d}-{dt:03d}-pcap-histories.csv', type=str)
    parser.add_argument('--year', default=2019, type=int, help='year to fetch histories for')
    parser.add_argument('--freq', choices=['m', 'w'], default='m', type=str, help='time period frequency')
    return parser.parse_args()


def main(stub: str, year: int, freq: str, force: bool):
    """
    Main script function.
    """
    try:
        frame: pd.DataFrame = {
            'w': finance.apis.pcap.histories.frame_for_each_week_in,
            'm': finance.apis.pcap.histories.frame_for_each_month_in,
        }[freq](stub=stub, year=year, force=force)
    except KeyError:
        raise NotImplementedError(freq) from None

    # show histories broken down by account
    formatters = {col: lambda value: f'{value:<25}' for col in frame.columns if frame.dtypes[col] == object}
    for account, histories in frame.groupby(by='accountName'):
        histories = histories[[col for col in histories.columns if col not in ['accountName', 'userAccountId']]]
        ynabframe = pd.DataFrame({
            'Date': histories['t1'], 'Payee': 'Market', 'Memo': '',
            'Amount': histories['dateRangePerformanceValueChange']
        })
        logging.debug('\n%s\n\n%s', account, histories.to_string(formatters=formatters, index=False, index_names=False))
        logging.debug('\n%s\n\n%s', account, ynabframe.to_string(formatters=formatters, index=False, index_names=False))
        logging.debug('\ntotal %12.2f', ynabframe.Amount.sum())


if __name__ == '__main__':
    finance.helpers.run(main, get_arguments)
