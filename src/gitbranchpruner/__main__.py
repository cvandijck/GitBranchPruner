import argparse
import logging
import os
from pathlib import Path

from gitbranchpruner import __version__
from gitbranchpruner.tools import get_repo, prune_untracked_git_branches

LOGGER = logging.getLogger(name='git-branch-pruner')


def main():
    parser = argparse.ArgumentParser(
        prog=f'git-branch-pruner {__version__}',
        description='Prune local branches without a remote',
    )
    parser.add_argument('--repo_dir', '-r', help='git directory')
    parser.add_argument('--fetch-prune', '-f', help='fetch prune first', action='store_true')
    parser.add_argument('--yes', '-y', help='confirm everything', action='store_true')

    args = parser.parse_args()
    repo_dir = args.repo_dir
    fetch_prune = args.fetch_prune
    yes_to_all = args.yes

    LOGGER.info(f'Running git-branch-pruner {__version__}')

    if not repo_dir:
        repo_dir = os.getcwd()

    repo_dir = Path(repo_dir).absolute()
    repo = get_repo(repo_dir)

    try:
        prune_untracked_git_branches(repo=repo, fetch_prune=fetch_prune, yes_to_all=yes_to_all)
    except Exception as e:
        LOGGER.error(e)
        exit()


if __name__ == '__main__':
    main()
