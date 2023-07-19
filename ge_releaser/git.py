import datetime as dt
from typing import Iterable, List

import git
import github
from github.PullRequest import PullRequest

from ge_releaser.constants import GxFile, FILES_TO_COMMIT


class GitService:
    def __init__(
        self,
        github_token: str,
        repo_name: str,
        trunk: str,
        remote: str,
    ) -> None:
        self._git = git.Repo()

        gh = github.Github(github_token)
        self._gh = gh.get_repo(repo_name)

        self._trunk = trunk
        self._remote = remote

    def get_tags(self) -> List[git.Tag]:
        return sorted(self._git.tags, key=lambda t: t.commit.committed_datetime)

    def tag_commit(self, commit: str, version: str) -> None:
        self._git.git.checkout(commit)
        self._git.git.tag("-a", version, "-m", f'"{version}"')

    def create_and_checkout_branch(self, branch_name: str) -> None:
        self._git.git.checkout("HEAD", b=branch_name)

    def checkout_and_pull_trunk(self) -> None:
        self._git.git.checkout(self._trunk)
        self._git.git.pull(self._remote, self._trunk)

    def _check_for_untracked_files(self) -> bool:
        return bool(self._git.untracked_files or self._git.unstaged_files)

    def verify_no_untracked_files(self) -> None:
        if self._check_for_untracked_files():
            raise ValueError("There are untracked files. Please make sure to run this step with a clean repo.")

    def stage_all_and_commit(self, message: str) -> None:
        self._git.git.add(FILES_TO_COMMIT)
        self._git.git.commit("-m", message, "--no-verify")

    def get_release_timestamp(self, version: str) -> dt.datetime:
        return self._gh.get_release(version).created_at

    def get_merged_prs(self) -> Iterable[PullRequest]:
        return self._gh.get_pulls(
            base=self._trunk, state="closed", sort="updated", direction="desc"
        )

    def push_branch_to_remote(self, branch: str, set_upstream: bool) -> None:
        args = []
        if set_upstream:
            args.append("--set-upstream")
        args += [self._remote, branch]
        self._git.git.push(*args)

    def create_pr(self, title: str, body: str, head: str) -> PullRequest:
        return self._gh.create_pull(
            title=title,
            body=body,
            head=head,
            base=self._trunk,
        )

    def create_release(self, version: str, message: str, draft: bool = False) -> None:
        self._gh.create_git_release(
            tag=version, name=version, message=message, draft=draft
        )

    def check_if_commit_is_part_of_trunk(self, commit: str) -> bool:
        return self._trunk in self._git.git.branch("--contains", commit)
