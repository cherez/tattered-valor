import random
import copy

class Genotype(object):
  def cross(self, other):
    new = self.__class__(random.choice([self.value, other.value]))
    new.mutate()
    return new

  def mutate(self):
    error = "mutate has not been implemented for %s" % self.__class__.name
    raise NotImplementedError(error)

  def __repr__(self):
    return str(self.value)

def integer(min = 0, max = 2**31-1):
  class Integer(Genotype):
    def __init__(self, value = None):
      self.value = value
      if self.value is None:
        self.value = random.randint(min, max)

    def mutate(self):
      self.value += random.randint(-1, 1)
      self.clamp()

    def clamp(self):
      if self.value < min:
        self.value = min
      if self.value > max:
        self.value = max

  return Integer

def permutation(*values):
  class Permutation(Genotype):
    def __init__(self, value = None):
      self.value = value
      if self.value is None:
        self.value = [i for i in values]
        random.shuffle(self.value)

    def mutate(self):
      old = random.randrange(0, len(values))
      new = random.randrange(0, len(values))
      v = self.value[old]
      del self.value[old]
      self.value.insert(new, v)

  return Permutation

def genome(**types):
  class Genome(Genotype):
    def __init__(self, value = None):
      if not value:
        value = {}
      self.value = value

    def mutate(self):
      for i in types.keys():
        self.values[i].mutate()

    def cross(self, other):
      values = {}
      for i in types.keys():
        values[i] = self.values[i].cross(other.values[i])
      return Genome(values)

    @property
    def value(self):
      return {i: self.values[i].value for i in types.keys()}

    @value.setter
    def value(self, values):
      self.values = {}
      for i in types.keys():
        if i in values:
          value = values[i]
        else:
          value = None
        self.values[i] = types[i](value)

  return Genome
