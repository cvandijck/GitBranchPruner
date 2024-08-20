import argparse
import logging

from gitbranchpruner import __version__
from gitbranchpruner.exceptions import CodedError, UnknownError

LOGGER = logging.getLogger(name='{{cookiecutter.package_name}}')


def prune_branches(yes_to_all: bool = False):
    LOGGER.info(f'Running {{cookiecutter.package_name}} {__version__}')

    try:
        # ADD YOUR CODE HERE
        ...
    except Exception as e:
        LOGGER.error(f'Unknown exception raised\n{str(e)}')
        raise UnknownError from e
    # ADD SPECIFIC EXCEPTIONS WITH ASSIGNED EXIT CODES

    LOGGER.info('Exiting successfully')


def main():
    parser = argparse.ArgumentParser(
        prog=f'git-branch-pruner {__version__}',
        description='Prune local branches without a remote',
    )
    parser.add_argument('--yes', '-y', help='confirm everything', action='store_true')

    args = parser.parse_args()
    yes_to_all = args.yes

    try:
        prune_branches(yes_to_all=yes_to_all)
    except CodedError as e:
        LOGGER.info(e)
        exit(e.exit_code)
    # HANDLE SPECIFIC EXCEPTIONS AND EXIT WITH THEIR EXIT CODES


if __name__ == '__main__':
    main()
