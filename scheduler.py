import battle
import config
import time
import threading
import random
from competitor import Competitor

def next_game():
  return str(random.randrange(2**31-1))

class MatchThread(threading.Thread):
  def __init__(self, match):
    self.match = match
    threading.Thread.__init__(self)


  def run(self):
    self.match.prepare()
    if self.match.winner:
      return
    self.match.run()

class Scheduler(object):
  def __init__(self):
    self.exit = False
    self.matches = []
    self.load_competitors()

  def load_competitors(self):
    lines = open('competitors.txt', 'r').readlines()
    lines = [i.strip() for i in lines]
    lines = sorted(set(lines))
    self.competitors = [Competitor.from_string(i) for i in lines]

  def schedule_match(self):
    raise NotImplementedError()

  def process_match(self, match):
    raise NotImplementedError()

  def run(self):
    self.load_competitors()
    #keep going if we have matches to finish those cleanly
    while not self.exit or self.matches:
      #add matches if there's an opening and we're not quitting
      while len(self.matches) < config.matches and not self.exit:
        new = self.schedule_match()
        if new is None:
          break
        new = MatchThread(new)
        self.matches.append(new)
        new.start()

      time.sleep(1)
      self.load_competitors()

      done = [i for i in self.matches if not i.is_alive()]
      for i in done:
        self.process_match(i.match)
        self.matches.remove(i)

  def start_cli(self):
    t = threading.Thread(target = self.cli)
    t.daemon = True
    t.start()

  def cli(self):
    while True:
      command = input("> ")
      command = command.split(' ')
      #TODO: Add interface to make commands.
      if command[0] == 'exit':
        print('Exiting')
        print('This will take until the last currently running game completes.')
        self.exit = True
      else:
        print('Unrecognized command:', command)



class RandomScheduler(Scheduler):
  """A simple scheduler for testing.
  Throws a random pair together to fight"""

  def process_match(self, match):
    pass

  def schedule_match(self):
    if not self.competitors:
      return None
    competitors = [random.choice(self.competitors) for i in range(2)]
    game = battle.Game(config.host, next_game())
    return battle.Match(competitors[0], competitors[1], game)
