Finance Scripts
===============

This is a set of scripts to download and analyze finance data.

The aim is to...

  1) download daily holdings automatically
  2) download historical data
  3) update YNAB accounts

Setup
=====

Clone the repository.

- This repository uses the [YNAB][ynab_api] API by [dmlerner].
- This repository uses the [Personal Capital][personalcapital] API by [haochi].

Create a conda environment.

```bash
conda env create -f environment.yml
conda activate FinanceScripts
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

Example
=======

```python
import pandas as pd
import dataclasses
import datetime


import finance.apis
import finance.scrapers


if __name__ == '__main__':
    # create API handler instance
    handler = finance.apis.pcap.PCAPHandler()

    # fetch all transaction objects
    transactions = finance.scrapers.pcap.TransactionsScraper(handler, t0=datetime.datetime.now(), dt=1)
    for transaction in transactions.objects:
        print(transaction)

    # create a dataframe from any dataclass based object
    tframe: pd.DataFrame = pd.DataFrame(dataclasses.asdict(t) for t in transactions.objects)
```

Apps
====

### python -m scraper.pcap.apps.marketvalue

A script to download the market value for an account.
The script is given a starting date and a time period freqency.
The rows of the resulting dataframe will display the market value at the timestamps.

```
cd ./workspace
conda activate FinanceScripts
python -m scraper.apps.pcap.marketvalue --start 2019-12-01 --freq W
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
[dmlerner]: https://github.com/dmlerner
[ynab_api]: https://github.com/dmlerner/ynab-api
[personalcapital]: https://github.com/haochi/personalcapital
