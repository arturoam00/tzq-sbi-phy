import argparse
import sys
from pathlib import Path

BASE_INFILE = argparse.ArgumentParser(add_help=False)
BASE_INFILE.add_argument(
    "infile",
    default=sys.stdin,
    type=argparse.FileType("r"),
    nargs="?",
    help="YAML file with configuration settings",
)

BASE_SETUP = argparse.ArgumentParser(add_help=False)
BASE_SETUP.add_argument(
    "setup_file", type=str, help="Setup .h5 file with morphing information"
)

BASE_DELPHES = argparse.ArgumentParser(add_help=False)
BASE_DELPHES.add_argument("proc_dir", type=str, help="The process directory path")
BASE_DELPHES.add_argument(
    "--root-files-dir",
    type=Path,
    help="Directory to store .root files",
    dest="root_files_dir",
)
