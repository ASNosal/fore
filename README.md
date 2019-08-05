# fore
Fore! is a console based PGA leaderboard that can be configured to display the current position and scores for a configurable selection of golfers. The data is scraped from the [ESPN Golf Leaderboard](https://www.espn.com/golf/leaderboard).

It is based on [jmstjordan/PGALiveLeaderboard](https://github.com/jmstjordan/PGALiveLeaderboard)

## Dependencies
Requires BeautifulSoup(bs4) and Requests (requests) python libraries.

```bash
pip install bs4 requests colorama
```

## Usage
Replace golfer names in golfers.txt with golfers to be tracked.

```bash
python fore.py
```

![image](https://user-images.githubusercontent.com/53181907/62486237-b581d500-b78c-11e9-81d8-f2b20588e76c.png)

## License
[MIT](https://choosealicense.com/licenses/mit/)