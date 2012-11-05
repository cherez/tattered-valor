import scheduler
import config
import battle
import itertools
import pickle
import os
import shutil
import gzip #Using gzip because the visualizer can read them
from collections import namedtuple

RoundRobinGame = namedtuple('RoundRobinGame', ['number', 'p1', 'p2', 'winner'])

class RoundRobinPairing(object):
  p1 = ''
  p2 = ''
  p1wins = 0
  p2wins = 0
  games = 0

class RoundRobinData(object):
  def __init__(self):
    self.games = []
    self.pairings = {}

  def get_pairing(self, p1, p2):
    p1, p2 = sorted(str(i) for i in (p1, p2))
    index = (p1, p2)
    if index not in self.pairings:
      pairing = RoundRobinPairing()
      pairing.p1, pairing.p2 = index
      self.pairings[index] = pairing
    return self.pairings[index]

class RoundRobinScheduler(scheduler.Scheduler):
  def __init__(self):
    try:
      self.data = pickle.load(open('roundrobin.dat', 'rb'))
    except:
      self.data = RoundRobinData()
    scheduler.Scheduler.__init__(self)

  def process_match(self, match):
    number = len(self.data.games)+1
    winner = match.competitors[match.winner]
    game = RoundRobinGame(number, match.competitors[0], match.competitors[1], winner)

    pairing = self.data.get_pairing(*match.competitors)
    if winner == pairing.p1:
      pairing.p1wins += 1
    else:
      pairing.p2wins += 1
    self.data.games.append(game)

    pickle.dump(self.data, open('roundrobin.dat', 'wb'), -1)
    self.dump_pairings()
    os.makedirs('round_robin_logs', exist_ok=True)
    dest = os.path.join('round_robin_logs', '%s.glog' % number)
    log = open(match.log, 'rb').read()
    out = gzip.open(dest, 'wb')
    out.write(log)

    shutil.copy(match.log, dest)

  def schedule_match(self):
    if len(self.competitors) < 2:
      return None
    pairings = itertools.combinations(self.competitors, 2)
    least_played = min(pairings, key=lambda x: self.data.get_pairing(*x).games)
    pairing = self.data.get_pairing(*least_played)
    pairing.games += 1
    game = battle.Game(config.host, scheduler.next_game())
    match = battle.Match(least_played[0], least_played[1], game)
    return match

  def dump_pairings(self):
    #So ugly. :(
    values = [[0 for i in range(len(self.competitors))] for j in range(len(self.competitors))]
    for i, x in enumerate(self.competitors):
      for j, y in enumerate(self.competitors):
        if j <= i:
          continue
        if i == j:
          values[i][j] = 0
        else:
          p = self.data.get_pairing(x, y)
          if p.p1wins + p.p2wins == 0:
            value = 0
          else:
            value = (20. * p.p1wins) / (p.p1wins + p.p2wins) - 10
          values[i][j] = value
          values[j][i] = -value
    rankings = sorted([i for i in range(len(self.competitors))], key= lambda x:sum(values[x]), reverse=True)
    matrix = [['' for i in range(len(self.competitors)+2)] for j in range(len(self.competitors)+1)]

    for i, x in enumerate(rankings):
      matrix[i+1][0] = str(self.competitors[x])
      matrix[0][i+1] = str(self.competitors[x])
      matrix[i+1][-1] = str(sum(values[x]))

      for j, y in enumerate(rankings):
        matrix[i+1][j+1] = str(values[x][y])

    matrix[0][-1] = 'Total'

    csv = '\n'.join([','.join(j for j in i) for i in matrix])
    f = open('pairings.csv', 'w')
    f.write(csv)
