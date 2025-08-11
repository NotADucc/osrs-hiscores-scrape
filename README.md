# OSRS Hiscore tool

# Requirements 
- Python 3.x [Download here](https://www.python.org/downloads/)
- Packages (possible I forgot some)
  - beautifulsoup4
  - fake-useragent
  - requests
  - requests[socks]

```console
pip install -r requirements.txt
# or
python -m pip install -r requirements.txt
```

# Main Features
- Pull a hiscore category and save the player names on a file.
- Filter usernames based on skills/bossing achievements and save that resultset on a file.
- Pull an individual's stats from OSRS hiscores.
- Analyse a highscore category (Count, total-, max- and min scores)

# Misc Features
- Sort the output, sorting script provided since scrape_hs is 'multi threaded'/async so the kvp resultset is not chronological.


> [!Note]
> Use apostrophes/quotes when you have an argument value that contains a space.
> Look at [Filter Codeblock](#Filterpy) for an example.

# Usage

## Filter.py
```console
py filter.py --in-file input.txt --out-file output.txt --account-type pure --filter 'ranged=50,attack<50'
py filter.py --in-file input.txt --out-file output.txt --account-type pure --filter 'ranged>50 , attack>=50'
py filter.py --in-file input.txt --out-file output.txt --account-type pure --filter 'ranged<=50, attack=50' 
```
| Argument      | Required | Description                                |
| ------------- | -------- | ------------------------------------------ |
| `--in-file`   | Yes      | Path to the input file                |
| `--out-file`  | Yes      | Path to the output file                    |
| `--proxy-file`  | No      | Path to the proxy file                    |
| `--start-nr`  | No      | Key value pair index that it should start filtering at |
| `--account-type`  | No      | Account type it should look at (default: 'regular') |
| `--filter`  | Yes      | Custom filter on what the accounts should have. |

## Scrape_hs.py
```console
py scrape_hs.py --out-file output.txt --account-type pure --hs-type zuk
```
| Argument      | Required | Description                                |
| ------------- | -------- | ------------------------------------------ |
| `--out-file`  | Yes      | Path to the output file                    |
| `--proxy-file`  | No      | Path to the proxy file                    |
| `--account-type`  | No      | Account type it should pull from (default: 'regular') |
| `--hs-type`  | No      | Hiscore category it should pull from (default: 'overall') |
| `--start-page-nr`  | No      | Hiscore page number it should start at (default: 1) |
| `--end-page-nr`  | No      | Hiscore page number it should end at (default: end of category) |
| `--num-workers`  | No      | Number of concurrent scraping threads |

## Lookup.py
```console
py lookup.py --name Cow31337Killer
```
| Argument      | Required | Description                                |
| ------------- | -------- | ------------------------------------------ |
| `--name`  | Yes      | Name you want to lookup                    |
| `--account-type`  | No      | Account type it should pull from (default: 'regular') |

## analyse_category.py
```console
py analyse_category.py --out-file output.txt --hs-type zuk
```
| Argument      | Required | Description                                |
| ------------- | -------- | ------------------------------------------ |
| `--out-file`  | Yes      | Path to the output file                    |
| `--proxy-file`  | No      | Path to the proxy file                    |
| `--hs-type`  | Yes      | Hiscore category it should pull from |


# Logging
A logger is used to report progress. A "done" message is logged once processing is complete.
