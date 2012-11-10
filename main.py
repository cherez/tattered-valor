#!/bin/env python3
import config

if __name__ == '__main__':
  s = config.scheduler
  s.start_cli()
  s.run()
