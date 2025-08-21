# OSRS Hiscore tool

# Requirements 
- Python 3.12.x or greater [Download here](https://www.python.org/downloads/) (3.11.x might be fine but not sure, change setup file if you run 3.11.x) 
- Certain py packages, run the command at [Get started](#Getstarted).

# Get started
```console
pip install -r requirements.txt -e .
# or
python -m pip install -r requirements.txt -e .
```

# Main Features
- Filter usernames based on skills/bossing achievements and save that resultset on a file.
- Analyse a highscore category (Count, total-, max- and min scores)
- Pull a hiscore category and save the player names on a file.

# Misc Features
- Pull an individual's stats from OSRS hiscores.
- Get maximum page of a hiscore category

> [!Note]
> Use apostrophes/quotes when you have an argument value that contains a space.
> Look at [Filter Codeblock](#filterpy) for an example.

# Usage

## filter.py

Scrape hiscores while filtering accounts based on category information (combat, skill levels, boss kc, etc.), filtered data gets saved to an output file.

```console
py .\scripts\filter.py --out-file output.txt --filter 'ranged=50,attack<50'
py .\scripts\filter.py --out-file output.txt --filter 'ranged>50 , attack>=50'
py .\scripts\filter.py --out-file output.txt --filter 'ranged<=50, attack=50' 
```
| Argument      | Required | Description                                |
| ------------- | -------- | ------------------------------------------ |
| `--out-file`  | Yes      | Path to the output file                    |
| `--proxy-file`  | No      | Path to the proxy file                    |
| `--rank-start`  | No      | Rank number that it should start filtering at (default: 1) |
| `--account-type`  | No      | Account type it should look at (default: 'regular') |
| `--hs-type`  | No      | Hiscore category it should pull from (default: 'overall') |
| `--filter`  | Yes      | Custom filter on what the accounts should have |
| `--num-workers`  | No      | Number of concurrent scraping threads (default: 15) |


## analyse_category.py

Aggregate hiscore data; saves total count, total kc/xp, first rank, and last rank, aggregated data gets saved to an output file.

```console
py .\scripts\analyse_category.py --out-file output.txt --hs-type zuk --account-type hc
```
| Argument      | Required | Description                                |
| ------------- | -------- | ------------------------------------------ |
| `--out-file`  | Yes      | Path to the output file                    |
| `--proxy-file`  | No      | Path to the proxy file                    |
| `--hs-type`  | Yes      | Hiscore category it should pull from        |
| `--account-type`  | Yes      | Account type it should pull from       |


## scrape_hs.py

Scrape hiscore category, scraped data gets saved to an output file.

```console
py .\scripts\scrape_hs.py --out-file output.txt --account-type pure --hs-type zuk
```
| Argument      | Required | Description                                |
| ------------- | -------- | ------------------------------------------ |
| `--out-file`  | Yes      | Path to the output file                    |
| `--proxy-file`  | No      | Path to the proxy file                    |
| `--account-type`  | No      | Account type it should pull from (default: 'regular') |
| `--hs-type`  | No      | Hiscore category it should pull from (default: 'overall') |
| `--rank-start`  | No      | Hiscore rank number it should start at (default: 1) |
| `--rank-end`  | No      | Hiscore rank number it should end at (default: end of category) |
| `--num-workers`  | No      | Number of concurrent scraping threads (default: 15) |


## lookup.py

Account hiscore lookup script, result gets printed on console.

```console
py .\scripts\lookup.py --name Cow1337Killer
```
| Argument      | Required | Description                                |
| ------------- | -------- | ------------------------------------------ |
| `--name`  | Yes      | Name you want to lookup                    |
| `--account-type`  | No      | Account type it should pull from (default: 'regular') |
| `--hs-type`  | No      | Filter on specific hiscore category  |


## max_page.py

Find the max page and rank of a category, result gets printed on console.

```console
py .\scripts\max_page.py --account-type hc --hs-type zuk
```
| Argument      | Required | Description                                |
| ------------- | -------- | ------------------------------------------ |
| `--account-type`  | Yes      | Account type it should scout   |
| `--hs-type`  | Yes      | Highscore Category it should scout  |


# Logging
A logger (and progressbar) is used to report progress. A "done" message is logged once processing is complete.
