import datetime as dt
import enum
import re
from collections import defaultdict
from typing import Dict, List, Tuple, cast

import click
import git
from github.Organization import Organization
from github.PullRequest import PullRequest
from github.Repository import Repository
from packaging import version

from ge_releaser.env import Environment
from ge_releaser.util import get_user_confirmation


class ChangelogCategory(enum.Enum):
    BREAKING = "BREAKING"
    FEATURE = "FEATURE"
    BUGFIX = "BUGFIX"
    DOCS = "DOCS"
    MAINTENANCE = "MAINTENANCE"
    UNKNOWN = "UNKNOWN"


class ChangelogCommit:
    def __init__(self, pr: PullRequest, github_org: Organization) -> None:
        if pr.title[0] == "[":
            try:
                self.pr_type, self.desc = re.match(
                    r"\[([a-zA-Z]+)\] ?(.*)", pr.title
                ).group(1, 2)
                self.pr_type = ChangelogCategory[self.pr_type.upper()]
                if self.pr_type not in ChangelogCategory:
                    self.pr_type = ChangelogCategory.MAINTENANCE
            except AttributeError:
                print(f"Couldn't parse PR title: {pr.title}")
                return
        else:
            self.pr_type = ChangelogCategory.MAINTENANCE
            self.desc = pr.title
        self.number = pr.number
        self.merge_timestamp = pr.merged_at
        self.attribution = (
            f" (thanks @{pr.user.login})"
            if not github_org.has_in_members(pr.user)
            else ""
        )

    def sort_key(self) -> Tuple[int, dt.datetime]:
        categories: Dict[ChangelogCategory, int] = {
            c: i + 1 for i, c in enumerate(ChangelogCategory)
        }
        return categories[self.pr_type], self.merge_timestamp

    def __str__(self) -> str:
        return (
            f"* [{self.pr_type.value}] {self.desc} (#{self.number}){self.attribution}"
        )


class ChangelogEntry:
    def __init__(
        self, github_org: Organization, pull_requests: List[PullRequest]
    ) -> None:
        changelog_commits: List[ChangelogCommit] = []
        for pr in pull_requests:
            changelog_commit: ChangelogCommit = ChangelogCommit(pr, github_org)
            changelog_commits.append(changelog_commit)

        changelog_commits.sort(key=ChangelogCommit.sort_key)
        self.commits = changelog_commits

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
        for commit in self.commits:
            rendered.append(f"{commit}\n")

        return rendered

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
                if category.value in commit.desc:
                    commit_by_category[category].append(commit)
                    added_commit = True
                    break

            if not added_commit:
                commit_by_category[ChangelogCategory.UNKNOWN].append(commit)

        return commit_by_category


def checkout_and_update_develop(git_repo: git.Repo) -> None:
    git_repo.git.checkout("develop")
    git_repo.git.pull("origin", "develop")


def parse_versions(version_number: str) -> Tuple[version.Version, version.Version]:
    current_version: version.Version
    with open(Environment.DEPLOYMENT_VERSION) as f:
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


def update_deployment_version_file(release_version: version.Version) -> None:
    with open(Environment.DEPLOYMENT_VERSION, "w") as f:
        f.write(f"{str(release_version).strip()}\n")


def update_changelogs(
    github_org: Organization,
    github_repo: Repository,
    current_version: version.Version,
    release_version: version.Version,
) -> None:
    relevant_prs: List[PullRequest] = _collect_prs_since_last_release(
        github_repo, current_version
    )

    changelog_entry: ChangelogEntry = ChangelogEntry(github_org, relevant_prs)

    changelog_entry.write(Environment.CHANGELOG_MD, current_version, release_version)
    changelog_entry.write(Environment.CHANGELOG_RST, current_version, release_version)


def _collect_prs_since_last_release(
    github_repo: Repository,
    current_version: version.Version,
) -> List[PullRequest]:
    last_release: dt.datetime = github_repo.get_release(str(current_version)).created_at
    merged_prs = github_repo.get_pulls(
        base="develop", state="closed", sort="updated", direction="desc"
    )
    recent_prs: List[PullRequest] = []
    for pr in merged_prs:
        if not pr.merged or "release candidate" in pr.title:
            continue
        # if we're seeing PRs merged more than a week before release, assume we've covered everything
        if pr.merged_at < (last_release - dt.timedelta(days=7)):
            break
        if pr.merged_at > last_release:
            recent_prs.append(pr)

    return recent_prs


def commit_changes(git_repo: git.Repo) -> None:
    git_repo.git.add(Environment.DEPLOYMENT_VERSION)
    git_repo.git.add(Environment.CHANGELOG_MD)
    git_repo.git.add(Environment.CHANGELOG_RST)
    git_repo.git.commit("-m", "release prep")


def create_pr(git_repo: git.Repo, github_repo: Repository, release_branch: str) -> str:
    git_repo.git.push("--set-upstream", "origin", release_branch)

    get_user_confirmation("\nAre you sure you want to open a PR [y/n]: ")

    timestamp: dt.date = dt.date.today()
    pr: PullRequest = github_repo.create_pull(
        title=f"release candidate {timestamp}",
        body=f"release prep for {timestamp}",
        head=release_branch,
        base="develop",
    )
    return f"https://github.com/great-expectations/great_expectations/pull/{pr.number}"


def prep(
    env: Environment,
    version_number: str,
) -> None:
    git_repo: git.Repo = env.git_repo
    github_repo: Repository = env.github_repo
    github_org: Organization = env.github_org

    breakpoint()
    click.secho("[prep]", bold=True, fg="blue")

    checkout_and_update_develop(git_repo)
    current_version, release_version = parse_versions(version_number)

    release_branch: str = create_and_checkout_release_branch(git_repo)
    click.secho(" * Created a release branch (1/5)", fg="yellow")

    update_deployment_version_file(release_version)
    click.secho(" * Updated deployment version file (2/5)", fg="yellow")

    update_changelogs(github_org, github_repo, current_version, release_version)
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
