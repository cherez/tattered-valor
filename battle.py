from collections import namedtuple
import time
import re
import gladiator

Game = namedtuple('Game', ['host', 'number'])


class Match(object):
  def __init__(self, c1, c2, game, type=gladiator.GitGladiator):
    self.competitors = c1, c2
    self.game = game
    self.status = 'new'
    self.winner = None
    self.log = None

    self.type = type

    self.make_gladiators()

  def make_gladiators(self):
    self.gladiators = []
    #TODO: Support for gladiators besides the git kind
    for i in self.competitors:
      args = i.split(' ')
      #first arg is a signature of the type
      args = args[1:]
      self.gladiators.append(self.type(*args))

  def prepare(self):
    self.status = 'preparing'
    for i in range(2):
      if not self.gladiators[i].prepare():
        self.winner = 1-i
        return False

    self.status = 'building'
    for i in range(2):
      if not self.gladiators[i].build():
        self.winner = 1-i
        return False
    return True

  def run(self):
    self.status = 'joining'
    for i in range(2):
      #give each client sufficient time to connect
      time.sleep(2)
      if not self.gladiators[i].run(self.game):
        self.winner = 1-i
        return False

    self.status = 'playing'
    while self.winner is None:
      time.sleep(1)
      for i in range(2):
        g = self.gladiators[i]
        if self.gladiators[i].poll():
          if g.crashed:
            self.winner = 1-i
            break
          else:
            self.log = g.log
            self.check_winner()
            break
    for g in self.gladiators:
      g.terminate()
    return self.winner

  def check_winner(self):
    log = open(self.log, 'r').read()
    match = re.search("\"game-winner\" (\d+) \"[^\"]+\" (\d+)", log)
    if match:
      self.winner = int(match.groups()[1])
    else:
      self.winner = -1
    return self.winner
