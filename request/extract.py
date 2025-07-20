from bs4 import BeautifulSoup

from request.common import CategoryRecord


def extract_highscore_records(page: bytes) -> list[CategoryRecord]:
    soup = BeautifulSoup(page, "html.parser")
    scores = soup.find_all(class_='personal-hiscores__row')

    result = []

    for score in scores:
        td_right = score.find_all('td', class_='right')

        rank = int(td_right[0].text.replace(',', '').strip())
        username = score.find('td', class_='left').a.text.strip()
        score = int(td_right[1].text.replace(',', '').strip())
        result.append(CategoryRecord(rank=rank, score=score, username=username))

    return result
