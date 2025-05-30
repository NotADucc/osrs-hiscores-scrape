# OSRS Hiscore tool

# Requirements 
- Python 3.x [Download here](https://www.python.org/downloads/)
- Packages (possible I forgot some)
  - beautifulsoup4
  - requests

```
pip install requests beautifulsoup4
# or
python -m pip install requests beautifulsoup4
```

# Main Features
- Pull a hiscore category and save the player names on a file.
- Filter usernames based on skills/bossing achievements and save that resultset on a file.
- Pull an individual his stats from OSRS hiscores.

# Misc Features
- Sort the output, sorting script provided since scrape_hs is 'multi threaded'/async so the kvp resultset is not chronological.
- Merge 2 outputs into one, this is for when a highscore type can't pull 100% of the data in 1 hiscore type but can in a different hiscore type.


> [!Note]
> Use apostrophes/quotes when you have an argument value that contains a space.
> Look at [Filter Codeblock](#Filter.py) for an example.

# Usage
## Filter.py
```
py filter.py --in-file input.txt --out-file output.txt --account-type pure --filter ranged:50,attack:50

py filter.py --in-file input.txt --out-file output.txt --account-type pure --filter 'ranged:50,attack:50'
py filter.py --in-file input.txt --out-file output.txt --account-type pure --filter 'ranged:50 , attack:50'
py filter.py --in-file input.txt --out-file output.txt --account-type pure --filter 'ranged : 50, attack : 50' 

py filter.py --in-file input.txt --out-file output.txt --account-type pure --filter "ranged:50,attack:50"
py filter.py --in-file input.txt --out-file output.txt --account-type pure --filter "ranged:50 , attack:50"
py filter.py --in-file input.txt --out-file output.txt --account-type pure --filter "ranged : 50, attack : 50" 
```
| Argument      | Required | Description                                |
| ------------- | -------- | ------------------------------------------ |
| `--in-file`   | Yes      | Path to the input file                |
| `--out-file`  | Yes      | Path to the output file                    |
| `--start-nr`  | No      | Key value pair index that it should start filtering at |
| `--method`  | No      | Either use osrs api or scrape from website |
| `--account-type`  | No      | Account type it should look at (default: 'regular') |
| `--filter`  | Yes      | Inclusive bound on what the account should have |
| `--delimiter` | No       | Delimiter used in the files (default: `,`) |
## Scrape_hs.py
```
py scrape_hs.py --out-file output.txt --account-type pure --hs-type zuk
```
| Argument      | Required | Description                                |
| ------------- | -------- | ------------------------------------------ |
| `--out-file`  | Yes      | Path to the output file                    |
| `--account-type`  | No      | Account type it should pull from (default: 'regular') |
| `--hs-type`  | No      | Hiscore category it should pull from (default: 'overall') |
| `--page-nr`  | No      | Hiscore page number it should start at |
## Lookup.py
```
py lookup.py --name Cow31337Killer
```
| Argument      | Required | Description                                |
| ------------- | -------- | ------------------------------------------ |
| `--name`  | Yes      | Name you want to lookup                    |
| `--account-type`  | No      | Account type it should pull from (default: 'regular') |
| `--method`  | No      | Either use osrs api or scrape from website |
## Sort.py
```
py sort.py --in-file input.txt
```
| Argument      | Required | Description                                |
| ------------- | -------- | ------------------------------------------ |
| `--in-file`   | Yes      | Path to the main file                |
| `--delimiter` | No       | Delimiter used in the files (default: `,`) |
# Merge.py
```
py merge.py --in-main main_file.txt --in-merge merge_file.txt --out-file output.txt
```
| Argument      | Required | Description                                |
| ------------- | -------- | ------------------------------------------ |
| `--in-main`   | Yes      | Path to the main input file                |
| `--in-merge`  | Yes      | Path to the file to merge in               |
| `--out-file`  | Yes      | Path to the output file                    |
| `--delimiter` | No       | Delimiter used in the files (default: `,`) |
# Debug.py
Can be ignored.

# Logging
A logger is used to report progress. A "done" message is logged once processing is complete.
