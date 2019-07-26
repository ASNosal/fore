import requests
from bs4 import BeautifulSoup
import json
import time
import os
import sys
import signal
from colorama import init
from colorama import Fore, Back, Style

#global variable
catch_count = 0
init()

def handler(signum, frame):
    global default_handler, catch_count
    catch_count += 1
    print (catch_count, 'Please Wait...')
    if catch_count > 2:
        # recover handler for signal.SIGINT
        signal.signal(signal.SIGINT, default_handler)
        print('***STOPPING***')

def create_player_file():
  new_golfers = input('Type first and last name of golfers separated by commas: ')
  player_file = open("golfers.txt", 'w+')
  for new_golfer in new_golfers.split(', '):
    player_file.write(str(new_golfer) + '\n')
  player_file.close()

def read_player_file():
  selected_players = []
  
  # create golfers.txt if it does not already exist
  if(not os.path.isfile("golfers.txt")):
    create_player_file()

  player_file = open("golfers.txt")
  for player in player_file:
    selected_players.append(player.rstrip("\n"))
  player_file.close()

  return selected_players

def add_new_golfer():
  new_golfer = input('Type first and last name of golfer: ')
  player_file = open("golfers.txt", 'a')
  player_file.write(str(new_golfer) + '\n')
  player_file.close()
  print(Fore.GREEN + str(new_golfer) + ' added!' + Fore.WHITE)
  return new_golfer

def remove_golfer():
  bye_golfer = input('Type first and last name of golfer to remove: ')
  if bye_golfer in selected_players:
    selected_players.remove(bye_golfer)
    print(Fore.RED + str(bye_golfer) + ' removed!' + Fore.WHITE)
  else:
    print(Fore.RED + bye_golfer + ' NOT IN YOUR LIST!' + Fore.WHITE)
    
  player_file = open("golfers.txt", 'w+')
  for dude in selected_players:
    player_file.write(str(dude) + '\n')
  player_file.close()

def get_players(soup, pos_col, player_col, score_col, today_col, thru_col, tee_time_col):
  rows = soup.find_all("tr", class_="Table2__tr")
  players = {}
  pos = ''
  score = ''
  today = ''
  thru = ''
  tee_time = ''
  for row in rows[1:]:
    cols = row.find_all("td")
    
    player = cols[player_col].text.strip()
    if(tee_time_col is None):
      pos = cols[pos_col].text.strip()
      score = cols[score_col].text.strip().upper()
      today = cols[today_col].text.strip().upper()
      thru = cols[thru_col].text.strip() if thru_col else "F"
      if score == 'CUT':
        players[player] = {'POS': pos, 'TO PAR': 'CUT', 'TODAY': '-', 'THRU': thru}
        continue
      elif score == 'WD':
        players[player] = {'POS': pos, 'TO PAR': 'WD', 'TODAY': '-', 'THRU': thru}
        continue
      elif score == 'DQ':
        players[player] = {'POS': pos, 'TO PAR': 'DQ', 'TODAY': '-', 'THRU': thru}
        continue
      elif score == 'E':
        players[player] = {'POS': pos, 'TO PAR': 0, 'TODAY': (int(today) if today.lstrip('+').lstrip('-').isdigit() else 0), 'THRU': thru}
      else:
        try:
          players[player] = {'POS': pos, 'TO PAR': int(score), 'TODAY': (int(today) if today.lstrip('+').lstrip('-').isdigit() else 0), 'THRU': thru}
        except ValueError:
          players[player] = {'POS': '?', 'TO PAR': '?', 'TODAY': '?', 'THRU': '?'}
    else:
      tee_time = cols[tee_time_col].text.strip()
      players[player] = {'TEE TIME': tee_time}
    
  return players

def ascii_art():
  print(Fore.GREEN + """\
         _______  _______  ______    _______  __  
        |       ||       ||    _ |  |       ||  | 
        |    ___||   _   ||   | ||  |    ___||  | 
        |   |___ |  | |  ||   |_||_ |   |___ |  | 
        |    ___||  |_|  ||    __  ||    ___||__| 
        |   |    |       ||   |  | ||   |___  __  
        |___|    |_______||___|  |_||_______||__|              
              """ + Fore.WHITE)

def get_col_indecies(soup):
  header_rows = soup.find_all("tr", class_="Table2__header-row")

  # ensure tournament data exists
  if len(header_rows) == 0 :
    print("No tournament data available at this time.")
    exit()

  # other possible entries for what could show up, add here.
  pos_fields = ['POS']
  player_fields = ['PLAYER']
  to_par_fields = ['TO PAR', 'TOPAR', 'TO_PAR']
  today_fields = ['TODAY']
  thru_fields = ['THRU']
  tee_time_fields = ['TEE TIME']

  header_col = header_rows[0].find_all("th")

  pos_col = None
  player_col = None
  score_col = None
  today_col = None
  thru_col = None
  tee_time_col = None

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
    if col_txt in today_fields:
      today_col = i
      continue
    if col_txt in thru_fields:
      thru_col = i
      continue
    if(col_txt in tee_time_fields):
      tee_time_col = i
      continue

  if player_col is None or (score_col is None and tee_time_col is None):
    print("Unable to track columns")
    exit()

  return pos_col, player_col, score_col, today_col, thru_col, tee_time_col


def verify_scrape(players):
  if len(players) < 25:
    print("Less than 25 players, seems suspucious, so exiting")
    exit()

  bad_entry_count = 0
  for key, value in players.items():
    if('TO PAR' in list(players.values())[0].keys()):
      scr = players[key]['TO PAR']
    else:
      scr = players[key]['TEE TIME']
    if scr == '?':
      bad_entry_count += 1
    if bad_entry_count > 0:
      print("Bad data entry, exiting")
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

  pos_col, player_col, score_col, today_col, thru_col, tee_time_col = get_col_indecies(soup)
  players = get_players(soup, pos_col, player_col, score_col, today_col, thru_col, tee_time_col)

  verify_scrape(players)

  data = {'Tournament': get_tournament_name(soup), 'IsActive': active, 'Players': players}

  return data,tee_time_col

def print_table_data(jdata,tee_time_col,selected_players):
  # determine number of columns
  n_cols = len(jdata['Players'][selected_players[0]].items()) + 1
  # determine width of potential columns
  w_player_col = 0
  for player in selected_players:
    if len(player) > w_player_col :
      w_player_col = len(player) + 1
  w_pos_col = len("POS") + 2
  w_scr_col = len("TO PAR") + 3
  w_today_col = len("TODAY") + 3
  w_thru_col = len("THRU    ") + 2

  #calculate table width and determine column headers
  w_table = w_player_col + len("TEE TIME") + 2
  w_table_offset = n_cols * 2 + 2
  col_header = "| " + (' ' * int(((w_player_col - 6)/2))) + "PLAYER" + (' ' * int(((w_player_col - 6)/2))) + " | TEE TIME |"
  if(n_cols > 2):
    w_table = w_player_col + w_pos_col + w_scr_col + w_today_col + w_thru_col
    col_header = "|  POS  |" + (' ' * int(((w_player_col - 6)/2))) + "PLAYER" + (' ' * round(((w_player_col - 6)/2))) + " |  TO PAR  |  TODAY  |   THRU    |"

  os.system('cls' if os.name == 'nt' else 'clear')
  player_print_cnt = 0
  #attempt to center tourney name
  print(Fore.GREEN + (' ' * int((w_table + w_table_offset - len(str(jdata['Tournament'])))/2)) + str(jdata['Tournament']))
  print(Fore.WHITE + '=' * (w_table + w_table_offset))
  print(col_header)
  for player,value in jdata['Players'].items():
    if(player in selected_players):
      print('-' * (w_table + w_table_offset))
      
      #Colorize score
      score = str(value["TO PAR"])
      score_offset = 0
      if int(score) < 0:
        score = Fore.RED + str(score) + Fore.WHITE
      elif int(score) > 0:
        score = Fore.CYAN + '+' + str(score) + Fore.WHITE
        score_offset = 1
      else:
        score = 'E'
      
      #Colorize today's score
      today = str(value["TODAY"])
      today_offset = 0
      if int(today) < 0:
        today = Fore.RED + str(today) + Fore.WHITE
      elif int(today) > 0:
        today = Fore.CYAN + '+' + str(today) + Fore.WHITE
        today_offset = 1
      else:
        today = 'E'
      
      #Colrize Thru
      thru = str(value["THRU"])
      if thru == 'F':
        thru = Fore.RED + thru + Fore.WHITE
      else:
        thru = str(thru)
      
      # print data row
      player_col_data = player +  (" " * (w_player_col - len(player)))
      if(tee_time_col is not None):
        tee_time = str(value["TEE TIME"])
        tee_time_col_data = (" " * (w_table - w_player_col - len(tee_time))) + tee_time
        print('| ' + player_col_data + ' |' + tee_time_col_data + ' |')
      else:
        pos_col_data = str(value["POS"]) + (' ' * (w_pos_col - len(str(value["POS"]))))
        scr_col_data = score + (' ' * (w_scr_col - len(str(value["TO PAR"]))- score_offset))
        today_col_data = today + (' ' * (w_today_col - len(str(value["TODAY"])) - today_offset))
        thru_col_data = thru + (' ' * (w_thru_col - len(str(value["THRU"]))))
        print('| ' + pos_col_data + ' |' + player_col_data + ' |' + scr_col_data + ' |' + today_col_data + ' |' + thru_col_data + ' |')
      player_print_cnt = player_print_cnt + 1
  # print horizontal divider below table
  print('=' * (w_table + w_table_offset))

run = True
#print(Style.BRIGHT + 'Fore!' + Style.NORMAL)
ascii_art()
time.sleep(1)
signal.signal(signal.SIGINT, handler)
default_handler = signal.getsignal(signal.SIGINT)

selected_players = read_player_file()

try:
  while run == True:
    jdata,tee_time_col = extract_json_data()
    print_table_data(jdata,tee_time_col,selected_players)
    
    # sleep for a minute unless an interrupt is caught
    for i in range(60):
      if catch_count == 0:
        time.sleep(1)
      else:
        continue
    
    if catch_count in range(1,3):
      
      command = input('Press G to add golfer to list, R to remove a golfer or Q to Quit: ')
      
      if command == 'G' or command =='g':
        selected_players.append(str(add_new_golfer()))
        catch_count = 0
        run = True
      
      elif command == 'Q' or command == 'q':
        ascii_art()
        #print('Fore!')
        raise KeyboardInterrupt
      
      elif command == 'R' or command =='r':
        remove_golfer()
        catch_count = 0
        run = True

      else:
        continue

    elif catch_count == 0:
      continue
    else:
      raise KeyboardInterrupt
    
except KeyboardInterrupt:
  pass
