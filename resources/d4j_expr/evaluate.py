import argparse
import json
import os
import numpy as np
from env import EvoD4jEnv
from main import loop, EvalException
from utils.metrics import *

num_versions = {
  'Lang': 65,
  'Chart': 26,
  'Time': 27,
  'Math': 106
}

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('--project', '-p', type=str, default=None)
  parser.add_argument('--tool', '-t', type=str, default='evosuite')
  parser.add_argument('--id', '-i', type=str, default='1')
  parser.add_argument('--selection', '-s', type=str, default="cEE")
  parser.add_argument('--noise', '-n', type=float, default=0.0)
  parser.add_argument('--verbose', '-v', action="store_true")
  parser.add_argument('--new', action="store_true")
  parser.add_argument('--skip-broken', action="store_true")
  args = parser.parse_args()

  assert 0.0 <= args.noise <= 1.0

  selection_metric = eval(args.selection)

  if args.project is None:
    projects = num_versions
  else:
    projects = {args.project: num_versions[args.project]}

  total = 0
  thresholds = [1, 3, 5, 10, 15, 20, 30]
  budgets = [3, 5, 10, 15, 20, 30]
  acc = {
    b: {t: 0 for t in thresholds}
    for b in budgets
  }
  exception_logs = {}
  for project in projects:
    for version in range(1, projects[project]+1):
      try:
        method_ranks = loop(project, version, args.tool, args.id, selection_metric,
                            budget=max(budgets), noise_prob=args.noise, new=args.new,
                            skip_broken=args.skip_broken, verbose=args.verbose)
        print(method_ranks)
      except EvalException as e:
        exception_logs[f"{project}-{version}"] = str(e)
        continue
      buggy_methods = method_ranks[method_ranks['is_buggy'] == True]
      for budget in budgets:
        b = budget
        while True:
          column = f"rank-{b}"
          if column in method_ranks.columns:
            last_ranks = buggy_methods[column].values
            break
          b -= 1
        for t in thresholds:
          if np.any(last_ranks <= t):
            acc[budget][t] += 1
      total += 1

  print(total)

  print(acc)

  with open(os.path.join(EvoD4jEnv.EVOSUITE_FL, args.id, "exception_logs.json"), "w") as json_file:
    json.dump(exception_logs, json_file)

  print(exception_logs)
