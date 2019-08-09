"""
A script to play with the various scrapers.
"""
import pandas as pd
import argparse
import logging


import scraper.handler
import scraper.apis


def get_arguments() -> argparse.Namespace:
    """
    Get the command line arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--force', action='store_true', help='force redownload?')
    return parser.parse_args()


def main(force=False):
    """
    The main script method.
    """
    handler = scraper.handler.PCHandler()

    # fetch all account objects
    accounts = scraper.apis.AccountsScraper(handler).reload(force=force)

    # fetch all holding objects
    holdings = scraper.apis.HoldingsScraper(handler).reload(force=force, accounts=accounts.objects)
    holdings.frame.to_csv(handler.config.getpath('{dt:%Y-%m-%d}-holdings.csv'), index=False)
    print(holdings.frame)


if __name__ == '__main__':
    # noinspection PyBroadException
    try:
        logging.basicConfig(level=logging.DEBUG, format='%(message)s')
        pd.set_option('display.max_colwidth', 1024)
        pd.set_option('display.max_columns', 1024)
        pd.set_option('display.max_rows', 1024)
        pd.set_option('display.width', 4096)
        opts = get_arguments()
        main(force=opts.force)
    except Exception:
        logging.exception('caught unhandled exception!')
        exit(-1)
    exit(0)
