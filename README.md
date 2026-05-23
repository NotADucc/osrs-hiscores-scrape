# OSRS Hiscore tool

A command-line web scraping tool for scraping Old School RuneScape (OSRS) hiscores data from the official Jagex hiscores pages.

# Requirements 
- Python 3.12.x or greater [Download here](https://www.python.org/downloads/) (3.11.x might be fine but not sure, change setup file if you run 3.11.x) 
- Certain py packages, run the command at [Get started](#Getstarted).

# Get started
```console
pip install -r requirements.txt .
pip install -r requirements.txt -e . # editable mode if u plan on modifying package
# or
python -m pip install -r requirements.txt .
python -m pip install -r requirements.txt -e . # editable mode if u plan on modifying package
```

# Main Features
- Filter usernames based on skills/bossing achievements and save that resultset to a file.
- Analyse a highscore category by creating some statistics like mean, median, min, max, quartiles and population/sample data.
- Fetch hiscore category pages and save the player names to a file.

# Misc Features
- Fetch an individual's stats from OSRS hiscores.
- Fetch maximum page of a hiscore category.
- Check if proxies are valid.

> [!Note]
> Use apostrophes (single quotes) or double quotes (depending on what shell u use) when you have an argument value that contains a space.
> Look at [Filter Codeblock](#filter_categorypy) for an example.

# Usage

## filter_category.py

Scrape hiscore pages while filtering accounts based on category information (combat, skill levels, boss kc, etc.), filtered player data gets saved to an output file.

```console
py .\scripts\filter_category.py --out-file output.txt --filter 'ranged=50,attack<50'
py .\scripts\filter_category.py --out-file output.txt --filter 'ranged>50 , attack>=50'
py .\scripts\filter_category.py --out-file output.txt --filter 'ranged<=50, attack=50' 
```
| Argument                                              | Required | Default Value | Description                                                               |
| ----------------------------------------------------- | -------- | ------------- | ------------------------------------------------------------------------- |
| `--out-file`                                          | Yes      | —             | Path to the output file                                                   |
| `--in-file`                                           | No       | `highscores`  | Path to the input file. Reads from `highscores` if omitted                |
| `--proxy-file`                                        | No       | —             | Path to the proxy file                                                    |
| [`--account-type`](./HSAccountTypes.md)               | No       | `regular`     | OSRS account type to scrape hiscores from                                 |
| [`--hs-type`](./HSTypes.md)                           | No       | `overall`     | OSRS hiscore category to scrape from                                      |
| `--filter`                                            | Yes      | —             | Custom filter used to match accounts                                      |
| `--rank-start`                                        | No       | `1`           | Starting rank number for scraping/filtering                               |
| `--num-workers`                                       | No       | `15`          | Number of concurrent scraping workers/threads                             |

## analyse_category.py

Aggregate hiscore data; saves total count, total kc/xp, first rank, and last rank, aggregated data gets saved to an output file.

```console
py .\scripts\analyse_category.py --out-file output.txt --hs-type zuk --account-type hc
```
| Argument                                | Required | Default Value | Description                          |
| --------------------------------------- | -------- | ------------- | ------------------------------------ |
| `--out-file`                            | Yes      | —             | Path to the output file              |
| `--proxy-file`                          | No       | —             | Path to the proxy file               |
| [`--hs-type`](./HSTypes.md)             | Yes      | `overall`     | OSRS hiscore category to scrape from |
| [`--account-type`](./HSAccountTypes.md) | Yes      | `regular`     | OSRS account type to scrape from     |


## fetch_pages.py

Scrape hiscore category pages, scraped names and scores gets saved to an output file.

```console
py .\scripts\fetch_pages.py --out-file output.txt --account-type pure --hs-type zuk
```
| Argument                                | Required | Default Value     | Description                            |
| --------------------------------------- | -------- | ----------------- | -------------------------------------- |
| `--out-file`                            | Yes      | —                 | Path to the output file                |
| `--proxy-file`                          | No       | —                 | Path to the proxy file                 |
| [`--account-type`](./HSAccountTypes.md) | Yes      | `regular`         | OSRS account type to scrape from       |
| [`--hs-type`](./HSTypes.md)             | No       | `overall`         | OSRS hiscore category to scrape from   |
| `--rank-start`                          | No       | `1`               | Starting hiscore rank to scrape from   |
| `--rank-end`                            | No       | `end of category` | Ending hiscore rank to scrape to       |
| `--num-workers`                         | No       | `15`              | Number of concurrent scraping workers  |

## fetch_user.py

Account hiscore lookup script, result gets printed on console.

```console
py .\scripts\fetch_user.py --name Cow1337Killer
```
| Argument                                | Required | Default Value | Description                          |
| --------------------------------------- | -------- | ------------- | ------------------------------------ |
| `--name`                                | Yes      | —             | OSRS player name to lookup           |
| [`--account-type`](./HSAccountTypes.md) | Yes      | `regular`     | OSRS account type to scrape from     |
| [`--hs-type`](./HSTypes.md)             | No       | `overall`     | Filter results by hiscore category   |


## fetch_max_page.py

Find the max page and rank of a category, result gets printed on console.

```console
py .\scripts\fetch_max_page.py --account-type hc --hs-type zuk
```
| Argument                                | Required | Default Value | Description                          |
| --------------------------------------- | -------- | ------------- | ------------------------------------ |
| [`--account-type`](./HSAccountTypes.md) | Yes      | `regular`     | OSRS account type to scrape from     |
| [`--hs-type`](./HSTypes.md)             | Yes      | `overall`     | OSRS hiscore category to scrape from |


## check_proxies.py

Proxy checker script, valid ones are written away and formatted as `http://user:password@ip:port`.

```console
py .\scripts\check_proxies.py --proxy-file proxy_file.txt
```
| Argument       | Required | Default Value | Description            |
| -------------- | -------- | ------------- | ---------------------- |
| `--proxy-file` | Yes      | —             | Path to the proxy file |


# Logging
Several log messages and progressbar is used to report progress.
