"""
A script to save a history CSVs for the date range.
"""
import datetime
import argparse
import logging


import scraper.apps.common
import scraper.handler
import scraper.config
import scraper.apis


from scraper.apps.common import yyyy_mm_dd


def get_arguments() -> argparse.Namespace:
    """
    Get the command line arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--force', action='store_true', help='force redownload?')
    parser.add_argument('--t0', default=datetime.datetime.now(tz=datetime.timezone.utc), type=yyyy_mm_dd)
    parser.add_argument('--dt', default=1, type=int, help='number of days after t0 to fetch')
    return parser.parse_args()


def main(force: bool, t0: datetime.datetime, dt: int):
    """
    The main script method.
    """
    handler = scraper.handler.PCHandler()

    # fetch all holding objects
    histories = scraper.apis.HistoriesScraper(handler, force=force, t0=t0, dt=dt)
    histories.frame.to_csv(handler.config.getpath(f'{t0:%Y-%m-%d}-{dt:03d}-histories.csv'), index=False)
    logging.debug('histories\n%s', histories.frame)


if __name__ == '__main__':
    scraper.apps.common.run(main, get_arguments)
