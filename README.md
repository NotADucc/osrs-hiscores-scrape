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
| Argument                                              | Required | Default Value     | Description                                                               |
| ----------------------------------------------------- | -------- | -------------     | ------------------------------------------------------------------------- |
| `--out-file`                                          | Yes      | —                 | Path to the output file                                                   |
| `--in-file`                                           | No       | `highscores`      | Path to the input file. Reads from `highscores` if omitted                |
| `--proxy-file`                                        | No       | —                 | Path to the proxy file                                                    |
| [`--account-type`](./HSAccountTypes.md)               | No       | `main`            | OSRS account type to scrape hiscores from                                 |
| [`--hs-type`](./HSTypes.md)                           | Yes      | —                 | OSRS hiscore category to scrape from                                      |
| `--filter`                                            | Yes      | —                 | Custom filter used to match accounts                                      |
| `--start-rank`                                        | No       | `1`               | Starting hiscore rank to scrape from                                      |
| `--end-rank`                                          | No       | `end of category` | Ending hiscore rank to scrape to                                          |
| `--num-workers`                                       | No       | `15`              | Number of concurrent scraping workers/threads                             |


## analyse_category.py
Aggregate hiscore data; saves total count, total kc/xp, first rank, and last rank, aggregated data gets saved to an output file.

```console
py .\scripts\analyse_category.py --out-file output.txt --hs-type psn --account-type main
```
| Argument                                | Required | Default Value | Description                                   |
| --------------------------------------- | -------- | ------------- | ------------------------------------          |
| `--out-file`                            | Yes      | —             | Path to the output file                       |
| `--proxy-file`                          | No       | —             | Path to the proxy file                        |
| [`--account-type`](./HSAccountTypes.md) | Yes      | —             | OSRS account type to scrape from              |
| [`--hs-type`](./HSTypes.md)             | Yes      | —             | OSRS hiscore category to scrape from          |
| `--num-workers`                         | No       | `15`          | Number of concurrent scraping workers/threads   |

### output example
```json
{
  "name": "phosanis_nightmare",
  "timestamp": "2025-09-21T16:45:03.458534+00:00",
  "count": 51929,
  "total_score": 13887495,
  "mean": 267.4323595678715,
  "median": 92,
  "population": {
    "variance": 325252.69053251523,
    "standard_deviation": 570.3092937455212,
    "skewness": 6.953565221418358,
    "kurtosis": 89.27937561873924
  },
  "sample": {
    "variance": 325258.9540645313,
    "standard_deviation": 570.3147850656962,
    "skewness": 6.953498268475899,
    "kurtosis": 89.27759858903298
  },
  "quartiles": {
    "q1": 28,
    "q2": 92,
    "q3": 255,
    "iqr": 227
  },
  "max": {
    "rank": 1,
    "score": 19109,
    "username": "View Poll"
  },
  "min": {
    "rank": 51929,
    "score": 5,
    "username": "Smokin Gear"
  }
}
```


## fetch_pages.py
Scrape hiscore category pages, scraped names and scores gets saved to an output file.

```console
py .\scripts\fetch_pages.py --out-file output.txt --account-type pure --hs-type zuk
```
| Argument                                | Required | Default Value     | Description                            |
| --------------------------------------- | -------- | ----------------- | -------------------------------------- |
| `--out-file`                            | Yes      | —                 | Path to the output file                |
| `--proxy-file`                          | No       | —                 | Path to the proxy file                 |
| [`--account-type`](./HSAccountTypes.md) | No       | `main`            | OSRS account type to scrape from       |
| [`--hs-type`](./HSTypes.md)             | No       | `overall`         | OSRS hiscore category to scrape from   |
| `--rank-start`                          | No       | `1`               | Starting hiscore rank to scrape from   |
| `--rank-end`                            | No       | `end of category` | Ending hiscore rank to scrape to       |
| `--num-workers`                         | No       | `15`              | Number of concurrent scraping workers  |


## fetch_user.py
Account hiscore lookup script, result gets printed on console.

```console
py .\scripts\fetch_user.py --name sewerslvt
```
| Argument                                | Required | Default Value | Description                          |
| --------------------------------------- | -------- | ------------- | ------------------------------------ |
| `--name`                                | Yes      | —             | OSRS player name to lookup           |
| [`--account-type`](./HSAccountTypes.md) | No       | `main`        | OSRS account type to scrape from     |
| [`--hs-type`](./HSTypes.md)             | No       | —             | Filter results by hiscore category   |

### output example
```json
{
 "username": "sewerslvt",
 "account_type": "main", # this is an assumption and can be wrong
 "de_ironed": true, # this is an assumption and can be wrong
 "dead_hc": true, # this is an assumption and can be wrong
 "timestamp": "2026-05-31T13:31:18.857909+00:00",
 "combat_lvl": 122.60000000000001,
 "skills": {
  "overall": { "lvl": 1911, "xp": 101502134, "rank": 669779 },
  "attack": { "lvl": 99, "xp": 13102183, "rank": 435671 },
  ... # truncated for readability
  "sailing": { "lvl": 49, "xp": 96286, "rank": 472668 }
 },
 "seasonal_modes": {
  "grid_points": { "score": 0, "rank": -1 },
  ... # truncated for readability
  "deadman_points": { "score": 0, "rank": -1 }
 },
 "clues": {
  "clue_all": { "score": 2, "rank": -1 },
  ... # truncated for readability
  "clue_master": { "score": 0, "rank": -1 }
 },
 "minigames": {
  "bh_hunter": { "score": 0, "rank": -1 },
  ... # truncated for readability
  "rifts_closed": { "score": 116, "rank": 401790 }
 },
 "misc": {
  "colosseum_glory": { "score": 0, "rank": -1 },
  "collections_logged": { "score": 109, "rank": -1 }
 },
 "bosses": {
  "abyssal_sire": { "score": 0, "rank": -1 },
  ... # truncated for readability
  "zulrah": { "score": 0, "rank": -1 }
 }
}
```


## fetch_max_page.py
Find the max page and rank of a category, result gets printed on console.

```console
py .\scripts\fetch_max_page.py --account-type hc --hs-type zuk
```
| Argument                                | Required | Default Value | Description                          |
| --------------------------------------- | -------- | ------------- | ------------------------------------ |
| [`--account-type`](./HSAccountTypes.md) | Yes      | —             | OSRS account type to scrape from     |
| [`--hs-type`](./HSTypes.md)             | Yes      | —             | OSRS hiscore category to scrape from |

### output example
```json
{
 "account_type": "hc",
 "category": "tzkal_zuk",
 "max_page": 50,
 "max_rank": 1239,
 "timestamp": "2026-05-31T13:37:58.400011+00:00"
}
```


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
