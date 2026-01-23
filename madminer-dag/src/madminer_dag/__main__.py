from .run import run
from .parse_args import parse_args
import sys

def main():
    sys.exit(run(parse_args(sys.argv[1:])))

if __name__ == "__main__":
    main()
