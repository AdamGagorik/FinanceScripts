"""
A script to save a holdings CSV for the current date.
"""
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
    return parser.parse_args()


def main(force=False):
    """
    The main script method.
    """
    handler = scraper.handler.PCHandler()

    # fetch all account objects
    accounts = scraper.apis.AccountsScraper(handler, force=force)

    # fetch all holding objects
    holdings = scraper.apis.HoldingsScraper(handler, force=force)
    holdings.frame.to_csv(handler.config.getpath('{dt:%Y-%m-%d}-holdings.csv'), index=False)
    logging.debug('holdings\n%s', holdings.frame)


if __name__ == '__main__':
    # noinspection PyBroadException
    try:
        scraper.config.logging()
        scraper.config.pandas()
        opts = get_arguments()
        main(force=opts.force)
    except Exception:
        logging.exception('caught unhandled exception!')
        exit(-1)
    exit(0)
