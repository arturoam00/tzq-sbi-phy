import sys

from madminer_cli.parse_args import parse_args
from madminer_cli.runner import Runner

sys.exit(Runner(parse_args(sys.argv[1:])).run())
