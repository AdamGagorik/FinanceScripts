"""
A script to save a history CSVs for the date range.
"""
import datetime
import argparse


import scraper.apis
import scraper.helpers


from scraper.helpers import yyyy_mm_dd


# noinspection DuplicatedCode
def get_arguments(args=None) -> argparse.Namespace:
    """
    Get the command line arguments.
    """
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--force', action='store_true', help='force redownload?')
    parser.add_argument('--stub', default='{t0:%Y-%m-%d}-{dt:03d}-histories.csv', type=str)
    parser.add_argument('--t0', default=datetime.datetime.now(tz=datetime.timezone.utc), type=yyyy_mm_dd)
    parser.add_argument('--dt', default=1, type=int, help='number of days after t0 to fetch')
    return parser.parse_args(args=args)


if __name__ == '__main__':
    scraper.helpers.run(scraper.apis.pcap.HistoriesScraper.export, get_arguments)
