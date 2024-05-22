import datetime as dt
import logging
from typing import Final, Generator, Iterable, List

import git
import github
from github.PullRequest import PullRequest

from ge_releaser.constants import GxFile

LOGGER: Final[logging.Logger] = logging.getLogger(__name__)


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

    @property
    def trunk(self) -> str:
        return self._trunk

    @property
    def trunk_is_0ver(self) -> bool:
        """
        Returns True if the trunk branch is named for a 0.x release.
        """
        return self._trunk.startswith("0.")

    def get_tags(self, reverse: bool = False) -> List[git.Tag]:
        """See also `.iter_tags()`"""
        return sorted(
            self._git.tags, key=lambda t: t.commit.committed_datetime, reverse=reverse
        )

    def iter_recent_tags(
        self, prefix_filter: str, limit: int = 2
    ) -> Generator[str, None, None]:
        """
        Iterate over tags that start with a given prefix, up to a limit.
        Useful for filtering out unrelated tags.
        """
        LOGGER.info(f"iter_tags: prefix_filter={prefix_filter}, limit={limit}")
        if limit < 1:
            raise ValueError("Limit must be greater than 0")
        itered: int = 0
        for tag in self.get_tags(reverse=True):
            LOGGER.debug(f"tag: {tag.name}")
            if itered >= limit:
                return
            if tag.name.startswith(prefix_filter):
                LOGGER.info(f"yielding tag: {tag.name}")
                yield tag.name
                itered += 1

    def tag_commit(self, commit: str, version: str) -> None:
        self._git.git.checkout(commit)
        self._git.git.tag("-a", version, "-m", f'"{version}"')

    def create_and_checkout_branch(self, branch_name: str) -> None:
        self._git.git.checkout("HEAD", b=branch_name)

    def checkout_and_pull_trunk(self) -> None:
        self._git.git.checkout(self._trunk)
        self._git.git.pull(self._remote, self._trunk)

    def _check_for_untracked_files(self) -> bool:
        return bool(self._git.untracked_files)

    def verify_no_untracked_files(self) -> None:
        if self._check_for_untracked_files():
            raise ValueError(
                "There are untracked files. Please make sure to run this step with a clean repo."
            )

    def stage_all_and_commit(self, message: str) -> None:
        files_to_commit = [
            GxFile.CHANGELOG_MD_V0 if self.trunk_is_0ver else GxFile.CHANGELOG_MD_V1,
            GxFile.DOCS_DATA_COMPONENT,
            GxFile.DOCS_CONFIG,
            GxFile.DEPLOYMENT_VERSION,
        ]
        self._git.git.add([file.value for file in files_to_commit])
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
