#!/bin/env python3
import scheduler
import round_robin
import config

if __name__ == '__main__':
  if config.scheduler == 'random':
    s = scheduler.RandomScheduler()
  elif config.scheduler == 'roundrobin':
    s = round_robin.RoundRobinScheduler()
  else:
    print('Unrecognized scheduler in config.')
    print('Using roundrobin instead.')
    s = round_robin.RoundRobinScheduler()
  s.start_cli()
  s.run()
