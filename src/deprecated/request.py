from bs4 import BeautifulSoup

from src.request.common import HSLookup
from src.request.request import https_request


def lookup_scrape(name: str, account_type: HSLookup) -> str:
    params = {'user1': name}
    page = https_request(account_type.personal(), params)
    return page


def extract_stats(page: bytes) -> dict:
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
