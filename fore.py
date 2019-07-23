import requests
from bs4 import BeautifulSoup
import json
import time
import os
import sys
import signal

def handler(signum, frame):
    global default_handler, catch_count
    catch_count += 1
    print (catch_count, 'Please Wait...')
    if catch_count > 2:
        # recover handler for signal.SIGINT
        signal.signal(signal.SIGINT, default_handler)
        print('***STOPPING***')

def get_players(soup, pos_col, player_col, score_col, thru_col):
  rows = soup.find_all("tr", class_="Table2__tr")
  players = {}
  for row in rows[1:]:
    cols = row.find_all("td")
    # If we get a bad row. For example, during the tournament we there
    # is a place holder row that represents the cut line
    if len(cols) < 5:
      continue
    pos = cols[pos_col].text.strip()
    player = cols[player_col].text.strip()
    score = cols[score_col].text.strip().upper()
    thru = cols[thru_col].text.strip() if thru_col else "F"
    if score == 'CUT':
      players[player] = {'POS': pos, 'TO PAR': 'CUT', 'THRU': thru}
      continue
    elif score == 'WD':
      players[player] = {'POS': pos, 'TO PAR': 'WD', 'THRU': thru}
      continue
    elif score == 'DQ':
      players[player] = {'POS': pos, 'TO PAR': 'DQ', 'THRU': thru}
      continue
    elif score == 'E':
      players[player] = {'POS': pos, 'TO PAR': 0, 'THRU': thru}
    else:
      try:
        players[player] = {'POS': pos, 'TO PAR': int(score), 'THRU': thru}
      except ValueError:
        players[player] = {'POS': '?', 'TO PAR': '?', 'THRU': '?'}
  return players


def get_col_indecies(soup):
  header_rows = soup.find_all("tr", class_="Table2__header-row")

  # other possible entries for what could show up, add here.
  pos_fields = ['POS']
  player_fields = ['PLAYER']
  to_par_fields = ['TO PAR', 'TOPAR', 'TO_PAR']
  thru_fields = ['THRU']

  header_col = header_rows[0].find_all("th")

  pos_col = None
  player_col = None
  score_col = None
  thru_col = None

  for i in range(len(header_col)):
    col_txt = header_col[i].text.strip().upper()
    if col_txt in pos_fields:
      pos_col = i
      continue
    if col_txt in player_fields:
      player_col = i
      continue
    if col_txt in to_par_fields:
      score_col = i
      continue
    if col_txt in thru_fields:
      thru_col = i
      continue

  if player_col is None or score_col is None:
    print("Unable to track columns")
    exit()

  return pos_col, player_col, score_col, thru_col


def verify_scrape(players):
  if len(players) < 25:
    print("Less than 25 players, seems suspucious, so exiting")
    exit()

  bad_entry_count = 0
  for key, value in players.items():
    scr = players[key]['TO PAR']
    if scr == '?':
      bad_entry_count += 1
    if type(scr) is int and (scr > 50 or scr < -50):
      print("Bad score entry, exiting")
      exit()

  if bad_entry_count > 3:
    # arbitrary number here, I figure this is enough bad entries to call it a bad pull
    print("Multiple bad entries, exiting")
    exit()


def get_tournament_name(soup):
  tournament_name = soup.find_all(
    "h1", class_="headline__h1 Leaderboard__Event__Title")[0].text
  return tournament_name


def extract_json_data():
  result = requests.get("http://www.espn.com/golf/leaderboard")
  soup = BeautifulSoup(result.text, "lxml")

  status = soup.find_all("div", class_="status")[0].find_all("span")[0].text.upper()
  active = 'FINAL' not in status

  pos_col, player_col, score_col, thru_col = get_col_indecies(soup)
  players = get_players(soup, pos_col, player_col, score_col, thru_col)

  verify_scrape(players)

  data = {'Tournament': get_tournament_name(soup), 'IsActive': active, 'Players': players}

  return data

run = True
catch_count = 0
signal.signal(signal.SIGINT, handler)
default_handler = signal.getsignal(signal.SIGINT)

selected_players = []
player_file = open("golfers.txt")
for player in player_file:
  selected_players.append(player.rstrip("\n"))
player_file.close()

try:
  while run == True:
    jdata = extract_json_data()
    os.system('cls' if os.name == 'nt' else 'clear')
    print(str(jdata['Tournament']))
    print('=================================')
    for player in selected_players:
      print(str(jdata['Players'][player]["POS"]) + " " + player)
      print("\tTO PAR: " + str(jdata['Players'][player]["TO PAR"]))
      print("\tTHRU:   " + str(jdata['Players'][player]["THRU"]))
    
    time.sleep(5)
    
    if catch_count in range(1,3):
      
      command = input('Press G to add golfer to list or Q to Quit: ')
      
      if command == 'G' or command =='g':
        new_golfer = input('Type first and last name of golfer: ')
        player_file = open("golfers.txt", 'a')
        player_file.write(str(new_golfer) + '\n')
        player_file.close()
        selected_players.append(str(new_golfer))
        print(str(new_golfer) + 'added!')
        catch_count = 0
        run = True
      
      elif command == 'Q' or command == 'q':
        raise KeyboardInterrupt

      else:
        continue

    elif catch_count == 0:
      continue
    else:
      raise KeyboardInterrupt
      run = False
    
except KeyboardInterrupt:
  pass
