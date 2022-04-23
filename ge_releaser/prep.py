import datetime as dt
import enum
import re
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple, cast

import click
import git
from github.Commit import Commit
from github.PullRequest import PullRequest
from github.Repository import Repository
from packaging import version

from ge_releaser.constants import (
    CHANGELOG_MD,
    CHANGELOG_RST,
    DEPLOYMENT_VERSION,
    TEAMS_YAML,
)


class ChangelogCategory(enum.Enum):
    BREAKING = "BREAKING"
    FEATURE = "FEATURE"
    BUGFIX = "BUGFIX"
    DOCS = "DOCS"
    MAINTENANCE = "MAINTENANCE"
    UNKNOWN = "UNKNOWN"


@dataclass
class ChangelogCommit:
    hash: str
    contents: str
    author: Optional[str]

    def __str__(self) -> str:
        value: str = f"* {self.contents}"
        if self.author is not None:
            value += f" (thanks @{self.author})"
        return value


class ChangelogEntry:
    def __init__(self, commits: List[ChangelogCommit]):
        self.commits = ChangelogEntry._sort_changelog_items_by_category(commits)

    def write(
        self,
        outfile: str,
        current_version: version.Version,
        release_version: version.Version,
    ) -> None:
        with open(outfile, "r") as f:
            contents: List[str] = f.readlines()

        insertion_point: int = 0
        for i, line in enumerate(contents):
            if str(current_version) in line:
                insertion_point = i - 1

        assert (
            insertion_point > 0
        ), "Could not find appropriate insertion point for new changelog entry"

        if outfile.endswith(".md"):
            contents[insertion_point:insertion_point] = self._render_to_md(
                release_version
            )
        elif outfile.endswith(".rst"):
            contents[insertion_point:insertion_point] = self._render_to_rst(
                release_version
            )
        else:
            raise Exception()

        with open(outfile, "w") as f:
            f.writelines(contents)

    def _render_to_md(self, release_version: version.Version) -> List[str]:
        rendered: List[str] = []
        title: str = f"\n### {release_version}\n"
        rendered.append(title)
        contents: List[str] = self._render_contents()
        rendered.extend(contents)
        return rendered

    def _render_to_rst(self, release_version: version.Version) -> List[str]:
        rendered: List[str] = []
        title: str = f"\n{release_version}\n"
        rendered.append(title)
        divider: str = "-----------------\n"
        rendered.append(divider)
        contents: List[str] = self._render_contents()
        rendered.extend(contents)
        return rendered

    def _render_contents(self) -> List[str]:
        rendered: List[str] = []
        for category in ChangelogCategory:
            commits: List[ChangelogCommit] = self.commits.get(category, [])
            for commit in commits:
                rendered.append(f"{commit}\n")

        return rendered

    def classify_unknowns(self) -> None:
        unassigned_commits: List[ChangelogCommit] = self.commits.get(
            ChangelogCategory.UNKNOWN, []
        )
        if unassigned_commits:
            for commit in unassigned_commits:
                print(f'\nSelect a classification for: "{commit.contents}"')

                response: int = 0
                while response not in [1, 2, 3, 4, 5]:
                    response = int(
                        input(
                            "  1) [BREAKING]\n  2) [FEATURE]\n  3) [BUGFIX]\n  4) [DOCS]\n  5) [MAINTENANCE]\n: "
                        )
                    )

                category: ChangelogCategory = [c for c in ChangelogCategory][
                    response - 1
                ]
                commit.contents = f"[{category.value}] {commit.contents}"
                self.commits[category].append(commit)

        del self.commits[ChangelogCategory.UNKNOWN]

    @staticmethod
    def _sort_changelog_items_by_category(
        changelog_commits: List[ChangelogCommit],
    ) -> Dict[ChangelogCategory, List[ChangelogCommit]]:
        commit_by_category: Dict[
            ChangelogCategory, List[ChangelogCommit]
        ] = defaultdict(list)

        for commit in changelog_commits:
            added_commit: bool = False
            for category in ChangelogCategory:
                if category.value in commit.contents:
                    commit_by_category[category].append(commit)
                    added_commit = True
                    break

            if not added_commit:
                commit_by_category[ChangelogCategory.UNKNOWN].append(commit)

        return commit_by_category


def checkout_and_update_develop(git_repo: git.Repo) -> None:
    git_repo.git.checkout("develop")
    git_repo.git.pull("origin", "develop")


def parse_versions(
    deployment_version_path: str, version_number: str
) -> Tuple[version.Version, version.Version]:
    current_version: version.Version
    with open(deployment_version_path) as f:
        contents: str = str(f.read()).strip()
        current_version = cast(version.Version, version.parse(contents))

    release_version: version.Version = cast(
        version.Version, version.parse(version_number)
    )
    assert release_version > current_version, "Version provided to command is not valid"

    return current_version, release_version


def create_and_checkout_release_branch(git_repo: git.Repo) -> str:
    branch_name: str = f"release-prep-{dt.date.today()}"
    git_repo.git.checkout("HEAD", b=branch_name)
    return branch_name


def update_deployment_version_file(
    deployment_version_path: str, release_version: version.Version
) -> None:
    with open(deployment_version_path, "w") as f:
        f.write(f"{str(release_version).strip()}\n")


def update_changelogs(
    git_repo: git.Repo,
    github_repo: Repository,
    current_version: version.Version,
    release_version: version.Version,
) -> None:
    changelog_commits: List[ChangelogCommit] = _collect_changelog_items(
        git_repo, github_repo, current_version
    )

    changelog_entry: ChangelogEntry = ChangelogEntry(changelog_commits)
    changelog_entry.classify_unknowns()

    changelog_entry.write(CHANGELOG_MD, current_version, release_version)
    changelog_entry.write(CHANGELOG_RST, current_version, release_version)


def _collect_changelog_items(
    git_repo: git.Repo, github_repo: Repository, current_version: version.Version
) -> List[ChangelogCommit]:
    changelog_contents: str = git_repo.git.log(
        "--oneline", "--no-abbrev-commit", f"{current_version}..HEAD"
    )

    core_team: Set[str] = _determine_core_team()

    changelog_commits: List[ChangelogCommit] = []
    for line in changelog_contents.split("\n"):
        commit_hash, title = line.split(" ", maxsplit=1)
        commit_details: Commit = github_repo.get_commit(commit_hash)
        author: Optional[str] = commit_details.author.login

        # Don't want attribution for core team
        if author in core_team:
            author = None

        changelog_commit: ChangelogCommit = ChangelogCommit(commit_hash, title, author)
        changelog_commits.append(changelog_commit)

    return changelog_commits


def _determine_core_team():
    with open(TEAMS_YAML, "r") as f:
        contents: str = f.read()

    core_team: Set[str] = set()

    r: re.Pattern = re.compile(r"@(\w+)")
    matches: List[str] = r.findall(contents)
    for name in matches:
        core_team.add(name)

    return core_team


def commit_changes(git_repo: git.Repo) -> None:
    git_repo.git.add(DEPLOYMENT_VERSION)
    git_repo.git.add(CHANGELOG_MD)
    git_repo.git.add(CHANGELOG_RST)
    git_repo.git.commit("-m", "release prep")


def create_pr(git_repo: git.Repo, github_repo: Repository, release_branch: str) -> str:
    git_repo.git.push("--set-upstream", "origin", release_branch)
    pr: PullRequest = github_repo.create_pull(
        title=release_branch,
        body=f"release prep for {dt.date.today()}",
        head=release_branch,
        base="develop",
    )
    return f"https://github.com/great-expectations/great_expectations/pull/{pr.number}"


def prep(
    git_repo: git.Repo,
    github_repo: Repository,
    version_number: str,
) -> None:
    click.secho("[prep]", bold=True, fg="blue")

    checkout_and_update_develop(git_repo)
    current_version, release_version = parse_versions(
        DEPLOYMENT_VERSION, version_number
    )

    release_branch: str = create_and_checkout_release_branch(git_repo)
    click.secho(" * Created a release branch (1/5)", fg="yellow")

    update_deployment_version_file(DEPLOYMENT_VERSION, release_version)
    click.secho(" * Updated deployment version file (2/5)", fg="yellow")

    update_changelogs(git_repo, github_repo, current_version, release_version)
    click.secho(" * Updated changelogs (3/5)", fg="yellow")

    commit_changes(git_repo)
    click.secho(" * Committed changes (4/5)", fg="yellow")

    url: str = create_pr(git_repo, github_repo, release_branch)
    click.secho(" * Opened prep PR (5/5)", fg="yellow")

    click.secho(
        f"\n[SUCCESS] Please review, approve, and merge PR before continuing to `cut` command",
        fg="green",
    )
    click.echo(f"Link to PR: {url}")
