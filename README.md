Personal Capital Scraper
========================

This is a script based on the [personalcapital] module by [haochi].

The aim is to...

  1) download daily holdings automatically
  2) download historical data
  3) update YNAB accounts

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
YNAB_APIKEY=[Your YNAB apikey]
```

- These variables may be set in a filed called `.env` in the run directory.
- Please note that the script will pause for 2-factor authentication on the 1st run.

Examples
========

```python
import pandas as pd
import dataclasses
import datetime


import scraper.handler
import scraper.apis


if __name__ == '__main__':
    # create API handler instance
    handler = scraper.handler.PCAPHandler()
    
    # fetch all account objects
    accounts = scraper.apis.pcap.AccountsScraper(handler)
    for account in accounts:
        print(account)
    
    # fetch all holding objects
    holdings = scraper.apis.pcap.HoldingsScraper(handler)
    for holding in holdings:
        print(holding)

    # fetch all history objects
    histories = scraper.apis.pcap.HistoriesScraper(handler, t0=datetime.datetime.now(), dt=1)
    for history in histories:
        print(history)

    # fetch all transaction objects
    transactions = scraper.apis.pcap.TransactionsScraper(handler, t0=datetime.datetime.now(), dt=1)
    for transaction in transactions:
        print(transaction)

    # create a dataframe from any dataclass based object
    vframe: pd.DataFrame = pd.DataFrame(dataclasses.asdict(v) for v in holdings)
    hframe: pd.DataFrame = pd.DataFrame(dataclasses.asdict(h) for h in histories)
    tframe: pd.DataFrame = pd.DataFrame(dataclasses.asdict(t) for t in transactions)
```

Apps
====

### python -m scraper.pcap.apps.holdings

This app will save a CSV file for the current date with all investment holdings.

```
cd ./workspace
conda activate PersonalCapitalScraper
python -m scraper.pcap.apps.holdings
```

### python -m scraper.pcap.apps.histories

This app will save a CSV file for history records in the time period for all investment accounts.

```
cd ./workspace
conda activate PersonalCapitalScraper
python -m scraper.pcap.apps.histories --t0 2019-08-10 --dt 1
```

### python -m scraper.pcap.apps.transactions

This app will save a CSV file for transactions in the time period for all accounts.

```
cd ./workspace
conda activate PersonalCapitalScraper
python -m scraper.pcap.apps.transactions --t0 2019-08-10 --dt 1
```

### python -m scraper.pcap.apps.joinhistories

This app will run the histories scraper at the specified freqency over the given year.
For example, use this to download the the balance change every week for a given account.

```
cd ./workspace
conda activate PersonalCapitalScraper
python -m scraper.apps.pcap.joinhistories --year 2019 --freq m
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

### fillna-accounts.yaml

The same logic is used as for fillna-holdings.

### fillna-histories.yaml

The same logic is used as for fillna-holdings.

### fillna-transactions.yaml

The same logic is used as for fillna-holdings.

[haochi]: https://github.com/haochi
[personalcapital]: https://github.com/haochi/personalcapital
