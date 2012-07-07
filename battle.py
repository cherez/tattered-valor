import subprocess
import tempfile
import shutil
from collections import namedtuple
import os

Game = namedtuple('Game', ['host', 'number'])

class Gladiator(object):
  def __init__(self):
    self.built = False
    self.process = None
    self.prepared = False
    self.done = False
    self.crashed = False

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
