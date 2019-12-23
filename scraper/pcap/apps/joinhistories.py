"""
A script to save a history CSV for each month in the given year.
"""
import pandas as pd
import argparse
import logging


import scraper.apis
import scraper.helpers


# noinspection DuplicatedCode
def get_arguments() -> argparse.Namespace:
    """
    Get the command line arguments.
    """
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--force', action='store_true', help='force redownload?')
    parser.add_argument('--year', default=2019, type=int, help='year to fetch histories for')
    return parser.parse_args()


def main(year: int, force: bool):
    """
    Main script function.
    """
    frame = scraper.apis.pcap.histories.frame_for_each_week_in(year=year, force=force)

    # show histories broken down by account
    for account, histories in frame.groupby(by='accountName'):
        rowsum = histories.groupby('accountName').agg(['sum']).droplevel(1, axis=1).reset_index()
        joined = pd.concat([histories, rowsum], ignore_index=True, sort=False)
        logging.debug('\n%s', joined)

    # show total sums over all accounts
    rowsum = frame.groupby('accountName').agg(['sum']).droplevel(1, axis=1).reset_index()
    logging.debug('total\n%s', rowsum)


if __name__ == '__main__':
    scraper.helpers.run(main, get_arguments)
