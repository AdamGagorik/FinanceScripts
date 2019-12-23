"""
A script to save a holdings CSV for the current date.
"""
import argparse


import scraper.apis
import scraper.helpers


# noinspection DuplicatedCode
def get_arguments() -> argparse.Namespace:
    """
    Get the command line arguments.
    """
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--force', action='store_true', help='force redownload?')
    parser.add_argument('--stub', default='{config.dt:%Y-%m-%d}-holdings.csv', type=str)
    return parser.parse_args()


if __name__ == '__main__':
    scraper.helpers.run(scraper.apis.pcap.HoldingsScraper.export, get_arguments)
