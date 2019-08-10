"""
A script to save a transaction CSVs for the date range.
"""
import datetime
import argparse
import logging


import scraper.handler
import scraper.config
import scraper.apis


def get_arguments() -> argparse.Namespace:
    """
    Get the command line arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--force', action='store_true', help='force redownload?')
    parser.add_argument('--t0', default=None, type=lambda v: datetime.datetime.strptime(v, '%Y-%m-%d'))
    parser.add_argument('--dt', default=1, type=lambda v: datetime.timedelta(days=int(v)))
    return parser.parse_args()


def main(force: bool, t0: datetime.datetime, dt: datetime.timedelta):
    """
    The main script method.
    """
    handler = scraper.handler.PCHandler()

    # fetch all holding objects
    transactions = scraper.apis.TransactionsScraper(handler).reload(force=force, t0=t0, dt=dt)
    transactions.frame.to_csv(handler.config.getpath('{dt:%Y-%m-%d}-transactions.csv'), index=False)
    logging.debug('transactions\n%s', transactions.frame)


if __name__ == '__main__':
    # noinspection PyBroadException
    try:
        scraper.config.logging()
        scraper.config.pandas()
        opts = get_arguments()
        main(opts.force, opts.t0, opts.dt)
    except Exception:
        logging.exception('caught unhandled exception!')
        exit(-1)
    exit(0)
