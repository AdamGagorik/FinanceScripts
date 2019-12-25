"""
A script to save a holdings CSV for the current date.
"""
import argparse


import finance.scrapers
import finance.helpers


# noinspection DuplicatedCode
def get_arguments() -> argparse.Namespace:
    """
    Get the command line arguments.
    """
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--force', action='store_true', help='force redownload?')
    parser.add_argument('--stub', default='{config.dt:%Y-%m-%d}-pcap-holdings.csv', type=str)
    return parser.parse_args()


if __name__ == '__main__':
    finance.helpers.run(finance.scrapers.pcap.HoldingsScraper.export, get_arguments)
