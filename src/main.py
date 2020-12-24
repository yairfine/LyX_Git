from argparse import ArgumentParser
from auto_git import *
from constants import *


def main():
    """Usage: auto_git.py [-h] (-c | -f <file_path>)
    """
    parser = ArgumentParser(description=DESCRIPTION, epilog=EPILOG)

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-c', '--config', action="store_true",
                       help=HELP_FIRST_CONFIG)
    group.add_argument('-f', '--file_path', action="store",
                       type=str, help=HELP_FILE_PATH, metavar=METAVAR_FILE_PATH)

    parser.add_argument('-d', '--debug', action="store_true")

    args = parser.parse_args()

    if args.debug:
        global INTERVAL_SECONDS
        INTERVAL_SECONDS = 10

    if args.config:
        first_config()
    else:
        start_track(args.file_path)


if __name__ == "__main__":
    main()
