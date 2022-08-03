## Usage
- This script is a python command line utility for scraping metadata from public youtube playlists so the playlist can be viewed/heard, without ads, using the free, open-source VLC Media Player

## Dependencies
- Pandas
- Selenium
- Chrome Driver
- bs4 / BeautifulSoup

## Instructions
- From the directory containing this script, activate a virtual environment that has Pandas, Selenium, and bs4 installed, then run `python -m ./code_converter.py` in the command prompt. 
- Input prompts will request a playlist url to scrape
- If the script cannot detect that chromedriver is installed in your venv path, it will offer to open the chromedriver download page in a browser
- If the script cannot detect that VLC is installed, it will offer to open the chromedriver download page in a browser

## Future Improvements
- Program will offer an option to download the playlist to your local disk