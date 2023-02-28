from __future__ import annotations

import datetime as dt

import git
import github
from github.PaginatedList import PaginatedList
from github.PullRequest import PullRequest
from packaging import version


class GitService:

    TRUNK = "develop"
    REMOTE = "origin"

    def __init__(self, github_token: str, repo_name: str) -> None:
        self._git = git.Repo()

        gh = github.Github(github_token)
        self._gh_repo = gh.get_repo(repo_name)

    def create_git_release(self, release_version: str, message: str) -> None:
        self._gh_repo.create_git_release(
            tag=release_version, name=release_version, message=message, draft=False
        )

    def tag_commit(self, commit: str, tag: str) -> None:
        if GitService.TRUNK not in self._git.git.branch("--contains", commit):
            raise ValueError(
                f"Selected commit is not a part of the '{GitService.TRUNK}' branch!"
            )

        self._git.git.checkout(commit)
        self._git.git.tag("-a", tag, "-m", f'"{tag}"')

    def push_to_remote(self, ref: str, set_upstream: bool = False) -> None:
        if set_upstream:
            self._git.git.push("--set-upstream", GitService.REMOTE, ref)
        else:
            self._git.git.push(GitService.REMOTE, ref)

    def get_release_and_current_versions(self) -> tuple[str, str]:
        tags = sorted(self._git.tags, key=lambda t: t.commit.committed_datetime)
        release_version = version.parse(str(tags[-1]))
        current_version = version.parse(str(tags[-2]))

        assert (
            release_version > current_version
        ), f"Version provided to command is not valid; {release_version} is not greater than {current_version}"

        return str(current_version), str(release_version)

    def checkout_and_update_trunk(self) -> None:
        self._git.git.checkout(GitService.TRUNK)
        self._git.git.pull(GitService.REMOTE, GitService.TRUNK)

    def create_and_checkout_branch(self, branch_name: str) -> None:
        self._git.git.checkout("HEAD", b=branch_name)

    def get_release_timestamp(self, release: str) -> dt.datetime:
        return self._gh_repo.get_release(release).created_at

    def get_merged_prs(self) -> PaginatedList[PullRequest]:
        return self._gh_repo.get_pulls(
            base=GitService.TRUNK, state="closed", sort="updated", direction="desc"
        )

    def add_all_and_commit(self, message: str) -> None:
        self._git.git.add(".")
        # Bypass pre-commit (if running locally on a dev env)
        self._git.git.commit("-m", message, "--no-verify")

    def create_pr(self, release_version: str, release_branch: str) -> PullRequest:
        return self._gh_repo.create_pull(
            title=f"[RELEASE] {release_version}",
            body=f"release prep for {release_version}",
            head=release_branch,
            base=GitService.TRUNK,
        )
