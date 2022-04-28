import datetime as dt
from typing import cast

import click
import git
from github.PullRequest import PullRequest
from github.Repository import Repository
from packaging import version

from ge_releaser.env import Environment
from ge_releaser.util import get_user_confirmation


def get_release_version() -> str:
    with open(Environment.DEPLOYMENT_VERSION) as f:
        contents: str = str(f.read()).strip()

    release_version: version.Version = cast(version.Version, version.parse(contents))
    return str(release_version)


def checkout_release_branch(git_repo: git.Repo) -> str:
    branch_name: str = f"release-prep-{dt.date.today()}"
    git_repo.git.checkout(branch_name)
    return branch_name


def cut_release(github_repo: Repository, release_branch: str, version: str) -> str:
    get_user_confirmation("\nAre you sure you want to cut the release [y/n]: ")
    pr: PullRequest = github_repo.create_pull(
        title=f"[RELEASE] {version}",
        body=f"Weekly release cut for {version}",
        head=release_branch,
        base="main",
    )
    return f"https://github.com/great-expectations/great_expectations/pull/{pr.number}"


def cut(env: Environment) -> None:
    git_repo: git.Repo = env.git_repo
    github_repo: Repository = env.github_repo

    click.secho("[cut]", bold=True, fg="blue")

    release_version: str = get_release_version()

    release_branch: str = checkout_release_branch(git_repo)
    click.secho(" * Checkout release branch (1/2)", fg="yellow")

    url: str = cut_release(github_repo, release_branch, release_version)
    click.secho(" * Open release PR (2/2)", fg="yellow")

    click.secho(
        f"\n[SUCCESS] Please wait for the build process and PyPI publishing to complete before moving to the `tag` cmd.",
        fg="green",
    )
    click.echo(f"Link to PR: {url}")
    click.echo(f"Link to Azure build: {Environment.AZURE_BUILDS}")
    click.echo(f"Link to PyPI page: {Environment.PYPI_PAGE}")
