#!/bin/env python3
import scheduler

if __name__ == '__main__':
  scheduler = scheduler.RandomScheduler()
  scheduler.start_cli()
  scheduler.run()
