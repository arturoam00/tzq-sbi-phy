from .run import run
from .parse_args import parse_args
import sys

sys.exit(run(parse_args(sys.argv[1:])))
