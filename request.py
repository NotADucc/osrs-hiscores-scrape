from common import HSType, HSCSVMapper, HSTableMapper, RequestFailed

import requests
from bs4 import BeautifulSoup

def get_hs_page(type = HSType.regular, table = HSTableMapper.overall, page_num = 1) :
    params = {'category_type': table.value[0], 'table': table.value[1], 'page': page_num, }
    page = https_request(type.value, params)
    
    return page
    
def https_request(url, params) :
    headers = {
       "Access-Control-Allow-Origin": "*",
       "Access-Control-Allow-Headers": "Origin, X-Requested-With, Content-Type, Accept"
    }
    
    resp = requests.get(url, headers=headers,params=params)

    content = resp.content
    
    if resp.status_code == 200 :
        return content
        
    raise RequestFailed(content, code=resp.status_code)
    
def extract_usernames(page) :
    soup = BeautifulSoup(page, "html.parser")
    scores = soup.find_all(class_='personal-hiscores__row')
    
    result = {}
    
    for score in scores :
        rank = int(score.find_all('td', class_='right')[0].text.replace(',', '').strip())
        username = score.find('td', class_='left').a.text.strip()
        result[rank] = username.replace('Ā', ' ').replace('\xa0', ' ')
    
    return result