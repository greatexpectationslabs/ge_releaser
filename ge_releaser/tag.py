import os

import click
import git

from ge_releaser.cli import GitEnvironment
from ge_releaser.constants import AZURE_BUILDS, PYPI_PAGE, RELEASES
from ge_releaser.util import checkout_and_update_develop, parse_deployment_version_file


def tag(env: GitEnvironment) -> None:
    click.secho("[tag]", bold=True, fg="blue")

    checkout_and_update_develop(env.git_repo)
    release_version: str = str(parse_deployment_version_file())

    _tag_latest_develop(env.git_repo, release_version)
    click.secho(" * Tagged latest commit on develop (1/2)", fg="yellow")

    _push_tag_to_remote(env.git_repo, release_version)
    click.secho(" * Pushed tag to remote (2/2)", fg="yellow")

    click.secho(
        f"\n[SUCCESS] Please ensure your tag is accurate before moving to the `release` command",
        fg="green",
    )

    tag_url: str = os.path.join(RELEASES, "tag", release_version)
    click.secho(
        f"\nPlease wait for the build process and PyPI publishing to complete before moving to the `release` cmd.",
        fg="green",
    )
    click.echo(f"Link to tag: {tag_url}")
    click.echo(f"Link to Azure build: {AZURE_BUILDS}")
    click.echo(f"Link to PyPI page: {PYPI_PAGE}")


def _tag_latest_develop(git_repo: git.Repo, release_version: str) -> None:
    git_repo.git.tag("-a", release_version, "-m", f'"{release_version}"')


def _push_tag_to_remote(git_repo: git.Repo, release_version: str) -> None:
    git_repo.git.push("origin", release_version)
