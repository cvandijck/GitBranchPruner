import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import git

LOGGER = logging.getLogger(name='git-branch-pruner')
BRANCH_INFO_RE = re.compile(r'^\*?\s+(?P<label>\S+)\s+(?P<commit>[0-9a-f]{7}) (?P<remote>\[.+\])?\s?(?P<message>.+)$')
UNTRACKED_RE = re.compile(r'\[\S*: gone\]')


@dataclass
class BranchInfo:
    label: str
    commit: str
    remote: Optional[str]
    message: str

    @property
    def has_remote(self) -> bool:
        return self.remote is not None

    @property
    def is_tracking(self) -> bool:
        return self.has_remote and UNTRACKED_RE.search(self.remote) is None


def get_repo(repo_dir: Optional[Path] = None) -> git.Repo:
    return git.Repo(repo_dir, search_parent_directories=repo_dir is None)


def retrieve_branches(repo: git.Repo) -> list[BranchInfo]:
    response = repo.git.branch('-vv')

    branch_info = []
    for branch_str in response.split('\n'):
        match = BRANCH_INFO_RE.match(branch_str)
        if not match:
            LOGGER.warning(f'could not parse "{branch_str}"')
            continue
        branch_info.append(BranchInfo(**match.groupdict()))
    return branch_info


def _user_confirm(prompt: str) -> bool:
    while True:
        user_input = input(f'{prompt} (y/n): ').strip().lower()
        if user_input in ['y', 'yes']:
            return True
        elif user_input in ['n', 'no']:
            return False


def prune_untracked_git_branches(repo: git.Repo, fetch_prune: bool = True, yes_to_all: bool = False):
    if fetch_prune:
        LOGGER.info('fetch with pruning')
        repo.git.fetch('--prune')

    branches = retrieve_branches(repo=repo)
    for branch in branches:
        if branch.has_remote and not branch.is_tracking:
            if not yes_to_all:
                remove_branch = _user_confirm(f'> prune branch "{branch.label}"')
            else:
                remove_branch = True

            if remove_branch:
                LOGGER.info(f'remove branch "{branch.label}"')
                repo.git.branch('-D', branch.label)
