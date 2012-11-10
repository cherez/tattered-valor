import scheduler
from competitor import GenomeCompetitor
import config
import battle
import os
import genome
import random
import pickle

competitor_count = 0

class CounterCompetitor(GenomeCompetitor):
  def __init__(self, repository, commit, genome):
    GenomeCompetitor.__init__(self, repository, commit, genome)
    global competitor_count
    competitor_count += 1
    self.id = competitor_count
    self.matches = 0
    self.wins = 0
    self.scheduled = 0


class CounterScheduler(scheduler.Scheduler):
  def __init__(self, champion, template, genome, matches=4):
    scheduler.Scheduler.__init__(self)
    os.makedirs('counter/results', exist_ok=True)
    self.champion = champion
    self.template = template
    self.genome = genome
    self.match_count = matches
    self.competitor = None

  def load_competitors(self):
    pass

  def schedule_match(self):
    if not self.competitor:
      self.make_competitor()
    self.competitor.scheduled += 1
    game = battle.Game(config.host, scheduler.next_game())
    args = [self.champion, self.competitor]
    random.shuffle(args)
    args.append(game)
    print(args)
    match = battle.Match(*args)
    if self.competitor.scheduled >= self.match_count:
      self.competitor = None
    return match

  def process_match(self, match):
    winner = match.competitors[match.winner]
    loser = match.competitors[1-match.winner]
    if winner == self.champion:
      challenger = loser
    else:
      challenger = winner
      winner.wins += 1
    challenger.matches += 1
    if challenger.matches >= self.match_count:
      self.dump_competitor(challenger)

  def dump_competitor(self, competitor):
    f = open('counter/results/%s-%s %s' %
        (competitor.wins, self.match_count - competitor.wins, competitor.id),
        'wb')
    pickle.dump(competitor.genome, f)

  def make_competitor(self):
    genome = self.genome()
    self.competitor = CounterCompetitor(
        self.template.repository,
        self.template.commit,
        self.genome.value)


