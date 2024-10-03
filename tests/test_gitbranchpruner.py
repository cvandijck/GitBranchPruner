import subprocess
import sys
from pathlib import Path

import git
import pytest

from gitbranchpruner.tools import prune_untracked_git_branches, retrieve_branches

PYTHON_EXE = sys.executable
NUM_TEST_BRANCHES = 3

SAFE_TEST_BRANCH_PREFIX = 'test/___tmp'
GIT_HEAD_FORMAT = '<git.Head "refs/heads/test/{}">'

REPO = git.Repo(Path(__file__).parent, search_parent_directories=True)


TEST_BRANCH_NAMES = [f'{SAFE_TEST_BRANCH_PREFIX}_{i}' for i in range(NUM_TEST_BRANCHES)]


def _add_test_branches(push_to_remote: bool):
    # get repo and active branch to reset
    active_branch = REPO.active_branch

    # create the test branches
    for branch_name in TEST_BRANCH_NAMES:
        new_head = REPO.create_head(branch_name)
        new_head.checkout()
        if push_to_remote:
            REPO.git.push('--set-upstream', 'origin', branch_name)

    # checkout the original active branch
    active_branch.checkout()


def _cleanup_test_branches(remove_from_remote: bool):
    # delete the test branches in case something went wrong
    for branch_name in TEST_BRANCH_NAMES:
        if remove_from_remote:
            REPO.git.push('-d', 'origin', branch_name)  # Delete remote
        REPO.delete_head(branch_name)


@pytest.fixture()
def repo_with_local_branches():
    _add_test_branches(push_to_remote=False)

    # yield the repo for testing
    yield REPO

    _cleanup_test_branches(remove_from_remote=False)


@pytest.fixture()
def repo_with_tracked_branches():
    _add_test_branches(push_to_remote=True)

    # yield the repo for testing
    yield REPO

    _cleanup_test_branches(remove_from_remote=True)


@pytest.fixture()
def repo_with_untracked_branches():
    _add_test_branches(push_to_remote=True)

    # delete the remote test branches
    for branch_name in TEST_BRANCH_NAMES:
        REPO.git.push('-d', 'origin', branch_name)  # Delete remote

    # yield the repo for testing
    yield REPO

    _cleanup_test_branches(remove_from_remote=False)


def test_import_package():
    """Test basic import of package."""
    import gitbranchpruner  # noqa: F401


@pytest.mark.console
def test_console_help():
    """Calls help file of console script and tests for failure."""
    process = subprocess.run(
        [PYTHON_EXE, '-m', 'gitbranchpruner', '--help'], capture_output=True, universal_newlines=True
    )
    assert process.returncode == 0, process.stderr


def test_local_branches(repo_with_local_branches: git.Repo):
    branches = retrieve_branches(repo_with_local_branches)
    assert set(TEST_BRANCH_NAMES).issubset({branch.label for branch in branches})

    for branch in branches:
        if branch.label == 'main':
            assert branch.has_remote is True
            assert branch.is_tracking is True

        if branch.label in TEST_BRANCH_NAMES:
            assert branch.has_remote is False
            assert branch.is_tracking is False


def test_tracked_branches(repo_with_tracked_branches: git.Repo):
    branches = retrieve_branches(repo_with_tracked_branches)
    assert set(TEST_BRANCH_NAMES).issubset({branch.label for branch in branches})

    for branch in branches:
        if branch.label == 'main':
            assert branch.has_remote is True
            assert branch.is_tracking is True

        if branch.label in TEST_BRANCH_NAMES:
            assert branch.has_remote is True
            assert branch.is_tracking is True


def test_untracked_branches(repo_with_untracked_branches: git.Repo):
    branches = retrieve_branches(repo_with_untracked_branches)
    assert set(TEST_BRANCH_NAMES).issubset({branch.label for branch in branches})

    for branch in branches:
        if branch.label == 'main':
            assert branch.has_remote is True
            assert branch.is_tracking is True

        if branch.label in TEST_BRANCH_NAMES:
            assert branch.has_remote is True
            assert branch.is_tracking is False


def _assert_branches_in_repo():
    repo_branch_names = [head.name for head in REPO.branches]
    for branch_name in TEST_BRANCH_NAMES:
        assert branch_name in repo_branch_names


def _assert_branches_not_in_repo():
    repo_branch_names = [head.name for head in REPO.heads]
    for branch_name in TEST_BRANCH_NAMES:
        assert branch_name not in repo_branch_names


def test_prune_local_branches(repo_with_untracked_branches: git.Repo):
    # assert test branch names are in the repo
    _assert_branches_in_repo()

    prune_untracked_git_branches(repo=repo_with_untracked_branches, fetch_prune=True, yes_to_all=True)

    # assert test branch names are still in the repo as they are local only
    _assert_branches_in_repo()


def test_prune_tracked_branches(repo_with_tracked_branches: git.Repo):
    # assert test branch names are in the repo
    _assert_branches_in_repo()

    prune_untracked_git_branches(repo=repo_with_tracked_branches, fetch_prune=True, yes_to_all=True)

    # assert test branch names are still in the repo as they are tracked
    _assert_branches_in_repo()


def test_prune_untracked_branches(repo_with_untracked_branches: git.Repo):
    # assert test branch names are in the repo
    _assert_branches_in_repo()

    prune_untracked_git_branches(repo=repo_with_untracked_branches, fetch_prune=True, yes_to_all=True)

    # assert test branch names are not in the repo as they are untracked
    _assert_branches_not_in_repo()
