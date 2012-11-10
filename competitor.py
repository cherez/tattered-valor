from gladiator import GitGladiator, GenomeGladiator
class Competitor(object):
  def __init__(self):
    pass
  def make_gladiator(self):
    raise NotImplementedError()

  @classmethod
  def from_string(cls, string):
    args = string.split(' ')
    if args[0] == 'git':
      args = args[1:]
      return GitCompetitor(*args)
    else:
      raise ValueError('unrecognized competitor type')

class GitCompetitor(Competitor):
  def __init__(self, repository, commit):
    self.repository = repository
    self.commit = commit
    Competitor.__init__(self)

  def make_gladiator(self):
    return GitGladiator(self.repository, self.commit)

  def __str__(self):
    return "git %s %s" % (self.repository, self.commit)

class GenomeCompetitor(Competitor):
  def __init__(self, repository, commit, genome):
    self.repository = repository
    self.commit = commit
    self.genome = genome
    Competitor.__init__(self)

  def make_gladiator(self):
    return GenomeGladiator(self.repository, self.commit, self.genome)
