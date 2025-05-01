# fore
Fore! is a console based PGA leaderboard that can be configured to display the current position and scores for a configurable selection of golfers. The data is scraped from the [ESPN Golf Leaderboard](https://www.espn.com/golf/leaderboard).

It is based on [jmstjordan/PGALiveLeaderboard](https://github.com/jmstjordan/PGALiveLeaderboard)

![image](https://user-images.githubusercontent.com/53181907/62486521-861f9800-b78d-11e9-8aa2-fe522ba961a0.png)

## Dependencies
Requires BeautifulSoup(bs4) and Requests (requests) python libraries.

```bash
pip install bs4 requests colorama
```

## Usage
Replace golfer names in golfers.txt with golfers to be tracked. Spelling errors will be corrected by fore.

```bash
python fore.py
```

## License
[MIT](https://choosealicense.com/licenses/mit/)
