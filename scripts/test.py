from src.request.common import HSAccountTypes, HSType
from src.util.io import build_temp_file

print(build_temp_file(account_type=HSAccountTypes.regular, hs_type=HSType.agility,
      file_path="D:\\Snogramming\\osrs-hiscore-scrape\\test.txt"))
input()
