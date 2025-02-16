from time import sleep
from common import HSType, HSTableMapper
from request import get_hs_page, extract_usernames

def retry(callback, name, idx, out_file): 
    retries, max_retries = 0, 3
    while retries < max_retries:
        try:
            callback(name, idx, out_file)
            break
        except Exception as err:
            print(err)
            print(f"Error occurred at nr {hs_nr}: {type(err)}. Retrying...")
            retries += 1
            sleep(10)
            if retries == max_retries:
                with open(out_file + '.err', "a") as fff:
                    fff.write('COULD NOT FIND %s,%s\n' % (idx, name))
                print('max retries reached')
                break