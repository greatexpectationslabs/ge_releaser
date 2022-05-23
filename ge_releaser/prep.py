import datetime as dt
import logging
import os
from typing import List, Tuple, cast

import click
import git
from github.Organization import Organization
from github.PaginatedList import PaginatedList
from github.PullRequest import PullRequest
from github.Repository import Repository
from packaging import version

from ge_releaser.changelog import ChangelogEntry
from ge_releaser.cli import GitEnvironment
from ge_releaser.constants import (
    CHANGELOG_MD,
    CHANGELOG_RST,
    DEPLOYMENT_VERSION,
    PULL_REQUESTS,
)
from ge_releaser.util import checkout_and_update_develop, parse_deployment_version_file


def prep(
    env: GitEnvironment,
    version_number: str,
) -> None:
    click.secho("[prep]", bold=True, fg="blue")

    checkout_and_update_develop(env.git_repo)
    current_version, release_version = _parse_versions(version_number)

    release_branch: str = _create_and_checkout_release_branch(
        env.git_repo, release_version
    )
    click.secho(" * Created a release branch (1/5)", fg="yellow")

    _update_deployment_version_file(release_version)
    click.secho(" * Updated deployment version file (2/5)", fg="yellow")

    _update_changelogs(
        env.github_org, env.github_repo, current_version, release_version
    )
    click.secho(" * Updated changelogs (3/5)", fg="yellow")

    _commit_changes(env.git_repo)
    click.secho(" * Committed changes (4/5)", fg="yellow")

    url: str = _create_pr(
        env.git_repo, env.github_repo, release_branch, release_version
    )
    click.secho(" * Opened prep PR (5/5)", fg="yellow")

    click.secho(
        f"\n[SUCCESS] Please review, approve, and merge PR before continuing to `tag` command",
        fg="green",
    )
    click.echo(f"Link to PR: {url}")


def _parse_versions(version_number: str) -> Tuple[str, str]:
    current_version: version.Version = parse_deployment_version_file()
    release_version: version.Version = cast(
        version.Version, version.parse(version_number)
    )
    assert release_version > current_version, "Version provided to command is not valid"

    return str(current_version), str(release_version)


def _create_and_checkout_release_branch(
    git_repo: git.Repo, release_version: str
) -> str:
    branch_name: str = f"release-{release_version}"
    git_repo.git.checkout("HEAD", b=branch_name)
    return branch_name


def _update_deployment_version_file(release_version: str) -> None:
    with open(DEPLOYMENT_VERSION, "w") as f:
        f.write(f"{release_version.strip()}\n")


def _update_changelogs(
    github_org: Organization,
    github_repo: Repository,
    current_version: str,
    release_version: str,
) -> None:
    relevant_prs: List[PullRequest] = _collect_prs_since_last_release(
        github_repo, current_version
    )

    changelog_entry: ChangelogEntry = ChangelogEntry(github_org, relevant_prs)

    changelog_entry.write(CHANGELOG_MD, current_version, release_version)
    changelog_entry.write(CHANGELOG_RST, current_version, release_version)


def _collect_prs_since_last_release(
    github_repo: Repository,
    current_version: str,
) -> List[PullRequest]:
    last_release: dt.datetime = github_repo.get_release(current_version).created_at
    merged_prs: PaginatedList[PullRequest] = github_repo.get_pulls(
        base="develop", state="closed", sort="updated", direction="desc"
    )
    recent_prs: List[PullRequest] = []

    # To ensure we don't accidently exit early, we set a threshold and wait to see a few old PRs before completing iteration
    counter: int = 0
    threshold: int = 5

    for pr in merged_prs:
        if counter >= threshold:
            break
        if not pr.merged:
            continue

        logging.info(pr, pr.merged_at, counter)
        if pr.merged_at < last_release:
            counter += 1
        if pr.merged_at > last_release:
            recent_prs.append(pr)

    return recent_prs


def _commit_changes(git_repo: git.Repo) -> None:
    git_repo.git.add(DEPLOYMENT_VERSION)
    git_repo.git.add(CHANGELOG_MD)
    git_repo.git.add(CHANGELOG_RST)
    git_repo.git.commit("-m", "release prep")


def _create_pr(
    git_repo: git.Repo,
    github_repo: Repository,
    release_branch: str,
    release_version: str,
) -> str:
    git_repo.git.push("--set-upstream", "origin", release_branch)

    pr: PullRequest = github_repo.create_pull(
        title=f"[RELEASE] {release_version}",
        body=f"release prep for {release_version}",
        head=release_branch,
        base="develop",
    )

    return os.path.join(PULL_REQUESTS, str(pr.number))
