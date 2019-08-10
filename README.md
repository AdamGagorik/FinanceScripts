Personal Capital Scraper
========================

This is a script based on the [personalcapital] module by [haochi].

The aim is to...

  1) download daily holdings automatically
  2) download historical data

Setup
=====

Create a conda environment.

```bash
conda env create -f environment.yml
conda activate PersonalCapitalScraper
```

Credentials
===========

Set the following environment variables.

```bash
PC_PASSWORD=[Your PC Password]
PC_USERNAME=[Your PC Username]
```

- These variables may be set in a filed called `.env` in the run directory.
- Please note that the script will pause for 2-factor authentication on the 1st run.

Examples
========

```python
import scraper.handler
import scraper.apis


if __name__ == '__main__':
    # create API handler instance
    handler = scraper.handler.PCHandler()
    
    # fetch all account objects
    accounts = scraper.apis.AccountsScraper(handler).reload()
    for account in accounts.objects:
        print(account)
    
    # fetch all holding objects
    holdings = scraper.apis.HoldingsScraper(handler).reload()
    for holding in holdings.objects:
        print(holding)
```

Apps
====

### python -m scraper.apps.holdings

This app will save a CSV file for the current date with all investment holdings.

```
# save holdings CSV as of today
cd ./workspace
conda activate PersonalCapitalScraper
python -m scraper.apps.holdings
```

### python -m scraper.apps.transactions

This app will save a CSV file for transactions in the time period for all accounts.

```
# save holdings CSV as of today
cd ./workspace
conda activate PersonalCapitalScraper
python -m scraper.apps.transactions --t0 2019-08-10 --dt 1
```

Filling Logic
=============

Fill in missing values by creating YAML based rule files in the run directory.

- The rules are a list of`where` and `value` mappings.
    - If all items from the `where` mapping match an instance's attributes...
        - The items from the `value` mapping will be set on the instance.

### fillna-holdings.yaml

```yaml
rules:
  - where:
      cusip: 'XXXXXXXXX'
      userAccountId: 00000000
    value:
      accountName: 'RothIRA'
      ticker: 'VTSAX'
```

[haochi]: https://github.com/haochi
[personalcapital]: https://github.com/haochi/personalcapital
