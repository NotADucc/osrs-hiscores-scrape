from common import calc_cmb, RequestFailed, HSOverall, HSLookup, HSApi, HSOverallTableMapper, HSApiCsvMapper

import requests
from bs4 import BeautifulSoup


def get_hs_page(type=HSOverall.regular, table=HSOverallTableMapper.overall, page_num=1):
    params = {'category_type': table.value[0],
              'table': table.value[1], 'page': page_num, }
    page = https_request(type.value, params)
    return page


def lookup(name, type=HSApi.regular):
    params = {'player': name}
    csv = https_request(type.value, params)
    return csv


def lookup_scrape(name, type=HSLookup.regular):
    params = {'user1': name}
    page = https_request(type.value, params)
    return page


def https_request(url, params):
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Origin, X-Requested-With, Content-Type, Accept"
    }

    resp = requests.get(url, headers=headers, params=params)

    content = resp.content

    if resp.status_code == 200:
        return content

    raise RequestFailed(content, code=resp.status_code)


def extract_stats(page):
    soup = BeautifulSoup(page, "html.parser")
    body = soup.find(id='contentHiscores')
    result = {}

    categories = body.find_all('tr')
    categories = categories[3:]

    skills = True
    for category in categories:
        soup = category.find_all('td')
        if len(soup) == 0:
            skills = False
            continue

        name = category.find('a').text.strip()
        if skills:
            result[name] = {
                'rank': int(soup[-3].text.replace(',', '').strip()),
                'lvl': int(soup[-2].text.replace(',', '').strip()),
                'xp': int(soup[-1].text.replace(',', '').strip())
            }
        else:
            result[name] = {
                'rank': int(soup[-2].text.replace(',', '').strip()),
                'score': int(soup[-1].text.replace(',', '').strip())
            }

    return result


def extract_usernames(page):
    soup = BeautifulSoup(page, "html.parser")
    scores = soup.find_all(class_='personal-hiscores__row')

    result = {}

    for score in scores:
        rank = int(score.find_all('td', class_='right')
                   [0].text.replace(',', '').strip())
        username = score.find('td', class_='left').a.text.strip()
        result[rank] = username.replace('Ā', ' ').replace('\xa0', ' ')

    return result
