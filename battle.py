import subprocess
import tempfile
import shutil
from collections import namedtuple
import os
import time
import re

Game = namedtuple('Game', ['host', 'number'])

class Gladiator(object):
  def __init__(self):
    self.built = False
    self.process = None
    self.prepared = False
    self.done = False
    self.crashed = False
    self.won = False
    self.log = None

    self.directory = tempfile.mkdtemp(prefix='gladiator')

  def __del__(self):
    try:
      shutil.rmtree(self.directory)
    except OSError:
      #not much to do here, I suppose
      #worth looking back here if this becomes an issue
      pass

  def prepare(self):
    raise NotImplementedError()

  def build(self):
    assert self.prepared
    subprocess.call(['make', 'clean'], cwd=self.directory,
        stdout=file("/dev/null", "w"),
        stderr=subprocess.STDOUT)

    result = subprocess.call(['make'], cwd=self.directory,
        stdout=file("/dev/null", "w"),
        stderr=subprocess.STDOUT) == 0

    if result:
      self.built = True

    return result

  def run(self, game):
    assert self.prepared
    if not self.built:
      if not self.build:
        return False

    self.game = game

    self.process = subprocess.Popen(['bash', 'run', game.host, game.number],
        stdout=file('/dev/null', 'w'),
        stderr=subprocess.STDOUT,
        cwd=self.directory)
    return True

  def poll(self):
    assert self.process
    result = self.process.poll()
    if result is None:
      return False
    self.done = True
    log_path = os.path.join(self.directory, 'python', '%s.gamelog' % self.game.number)
    if not os.path.exists(log_path):
      self.crashed = True
    else:
      self.log = log_path
    return True

  def terminate(self):
    if self.process:
      try:
        self.process.terminate()
      except OSError:
        pass

class GitGladiator(Gladiator):
  def __init__(self, repository, commit):
    self.repository = repository
    self.commit = commit
    Gladiator.__init__(self)

  def prepare(self):
    if self.prepared:
      return True
    result = subprocess.call(['git', 'clone',
      self.repository, self.directory],
      stdout=file('/dev/null', 'w'),
      stderr=subprocess.STDOUT)
    if result != 0:
      return False
    result = subprocess.call(['git', 'checkout', self.commit],
        stdout=file('/dev/null', 'w'),
        stderr=subprocess.STDOUT,
        cwd=self.directory)
    if result != 0:
      return False
    self.prepared = True
    return True

class Match(object):
  def __init__(self, c1, c2, game):
    self.competitors = c1, c2
    self.game = game
    self.status = 'new'
    self.winner = None

    self.make_gladiators()

  def make_gladiators(self):
    self.gladiators = []
    #TODO: Support for gladiators besides the git kind
    for i in self.competitors:
      args = i.split(' ')
      #first arg is a signature of the type
      args = args[1:]
      self.gladiators.append(GitGladiator(*args))

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
            self.check_winner(g.log)
            break
    for g in self.gladiators:
      g.terminate()
    return self.winner

  def check_winner(self, logfile):
    log = file(logfile, 'r').read()
    match = re.search("\"game-winner\" (\d+) \"[^\"]+\" (\d+)", log)
    if match:
      self.winner = int(match.groups()[1])
    else:
      self.winner = -1
    return self.winner
