"""
A script to save an account CSV.
"""
import argparse


import scraper.apis
import scraper.helpers


# noinspection DuplicatedCode
def get_arguments(args=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--force', action='store_true', help='force redownload?')
    parser.add_argument('--stub', default='{config.dt:%Y-%m-%d}-ynab-accounts.csv', type=str)
    parser.add_argument('--budget-id', dest='budget_id', default='last-used', help='budget to fetch accounts for')
    return parser.parse_args(args=args)


if __name__ == '__main__':
    scraper.helpers.run(scraper.apis.ynab.AccountsScraper.export, get_arguments)
