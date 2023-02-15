import datetime as dt
import logging
import os
from typing import List, Tuple

import click
import git
from github.PaginatedList import PaginatedList
from github.PullRequest import PullRequest
from github.Repository import Repository
from packaging import version

from ge_releaser.changelog import ChangelogEntry
from ge_releaser.cmd.util import checkout_and_update_develop
from ge_releaser.constants import GxFile, GxURL
from ge_releaser.git import GitEnvironment


def prep(env: GitEnvironment) -> None:
    click.secho("[prep]", bold=True, fg="blue")

    last_version, release_version = _parse_versions(env.git_repo)

    checkout_and_update_develop(env.git_repo)

    release_branch: str = _create_and_checkout_release_branch(
        env.git_repo, release_version
    )
    click.secho(" * Created a release branch (1/6)", fg="yellow")

    _update_deployment_version_file(release_version)
    click.secho(" * Updated deployment version file (2/6)", fg="yellow")

    _update_docs_component(last_version=last_version, release_version=release_version)
    click.secho(" * Updated version in docs data component (3/6)", fg="yellow")

    _update_changelogs(
        github_repo=env.github_repo,
        last_version=last_version,
        release_version=release_version,
    )
    click.secho(" * Updated changelogs (4/6)", fg="yellow")

    _commit_changes(env.git_repo)
    click.secho(" * Committed changes (5/6)", fg="yellow")

    url: str = _create_pr(
        git_repo=env.git_repo,
        github_repo=env.github_repo,
        release_branch=release_branch,
        release_version=release_version,
    )
    click.secho(" * Opened prep PR (6/6)", fg="yellow")

    _print_next_steps(url)


def _parse_versions(
    git_repo: git.Repo,
) -> Tuple[str, str]:
    tags = sorted(git_repo.tags, key=lambda t: t.commit.committed_datetime)
    release_version = version.parse(str(tags[-1]))
    last_version = version.parse(str(tags[-2]))

    assert release_version > last_version, "Version provided to command is not valid"

    return str(last_version), str(release_version)


def _create_and_checkout_release_branch(
    git_repo: git.Repo, release_version: str
) -> str:
    branch_name: str = f"release-{release_version}"
    git_repo.git.checkout("HEAD", b=branch_name)
    return branch_name


def _update_deployment_version_file(release_version: str) -> None:
    with open(GxFile.DEPLOYMENT_VERSION, "w") as f:
        f.write(f"{release_version.strip()}\n")


def _update_docs_component(last_version: str, release_version: str) -> None:
    """Updates the JSX file in our docs directory responsible for tracking GX and Python versions.

    It looks something like this:
    ```jsx
    export default {
      release_version: 'great_expectations, version 0.15.48',
      min_python: 'Python 3.7',
      max_python: 'Python 3.10'
    }
    ```
    """
    with open(GxFile.DOCS_DATA_COMPONENT, "r+") as f:
        contents = f.read()
        contents = contents.replace(last_version, release_version)
        f.write(contents)


def _update_changelogs(
    github_repo: Repository,
    last_version: str,
    release_version: str,
) -> None:
    relevant_prs: List[PullRequest] = _collect_prs_since_last_release(
        github_repo, last_version
    )

    changelog_entry: ChangelogEntry = ChangelogEntry(relevant_prs)

    changelog_entry.write(GxFile.CHANGELOG_MD, last_version, release_version)
    changelog_entry.write(GxFile.CHANGELOG_RST, last_version, release_version)


def _collect_prs_since_last_release(
    github_repo: Repository,
    last_version: str,
) -> List[PullRequest]:
    # 20220923 - Chetan - Currently, this grabs all PRs from the last release until the moment of program execution.
    # This should be updated so the changelog generation stops once it hits the release commit.

    last_release: dt.datetime = github_repo.get_release(last_version).created_at

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

        # Ignore closed PRs and any release-specific PRs
        if not pr.merged or "RELEASE" in pr.title:
            continue

        logging.info(pr, pr.merged_at, counter)
        if pr.merged_at < last_release:
            counter += 1
        if pr.merged_at > last_release:
            recent_prs.append(pr)

    return recent_prs


def _commit_changes(git_repo: git.Repo) -> None:
    git_repo.git.add(".")
    # Bypass pre-commit (if running locally on a dev env)
    git_repo.git.commit("-m", "release prep", "--no-verify")


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

    return os.path.join(GxURL.PULL_REQUESTS, str(pr.number))


def _print_next_steps(url: str) -> None:
    click.secho(
        f"\n[SUCCESS] Please review, approve, and merge PR before continuing to `publish` command",
        fg="green",
    )
    click.echo(f"Link to PR: {url}")
