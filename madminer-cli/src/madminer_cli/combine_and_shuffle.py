#!/bin/env python3

import argparse
import sys
from typing import List


def main() -> None:

    parser = argparse.ArgumentParser(
        prog="combine_and_shuffle",
        description="Combine and shuffle give .h5 `madminer` files",
    )
    parser.add_argument("files", nargs="+", help="Files to be combined and shuffled")
    parser.add_argument("outfile", type=str, help="Name of output file")

    arguments = parser.parse_args()

    outfile = arguments.outfile.rstrip(".h5") + ".h5"

    from madminer.sampling import combine_and_shuffle

    combine_and_shuffle(input_filenames=arguments.files, output_filename=outfile)


if __name__ == "__main__":
    main()
