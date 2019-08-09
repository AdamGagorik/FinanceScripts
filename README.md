Personal Capital Scraper
========================

This is a script based on the [personalcapital] module by [haochi].

Setup
=====

* Create a conda environment.

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

These variables may be set in a filed called `.env` in the run directory.

Examples
========

```python
import scraper.handler
import scraper.apis


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

This app will save a CSV file for the current date with all investment holdings.

```
# save holdings CSV as of today
cd ./workspace
activate PersonalCapitalScraper
python -m scraper.apps.holdings
```

Filling Logic
=============

Fill in missing values by creating YAML based rule files in the run directory.
The rules are a list of`where` and `value` mappings.
For example, if all items from the `where` mapping match an instance's attributes, the items from the `value` mapping will be set on the instance.

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
