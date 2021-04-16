import os
import argparse
from utils.cobertura import parse as parse_cobertura

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('path', type=str)
  parser.add_argument('--output', '-o', default='classes.trigger')
  args = parser.parse_args()

  _, covered_classes = parse_cobertura(args.path)
  with open(args.output, 'a') as f:
    f.write("\n".join(covered_classes)+"\n")
