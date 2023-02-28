import os

import click

from ge_releaser.constants import GxURL
from ge_releaser.git import GitService


def tag(git_service: GitService, commit: str, version_number: str) -> None:
    click.secho("[tag]", bold=True, fg="blue")

    _tag_release_commit(
        git_service=git_service, commit=commit, release_version=version_number
    )
    click.secho(f" * Tagged commit '{commit}' on develop (1/2)", fg="yellow")

    _push_tag_to_remote(git_service=git_service, release_version=version_number)
    click.secho(" * Pushed tag to remote (2/2)", fg="yellow")

    _print_next_steps(version_number)


def _tag_release_commit(
    git_service: GitService, commit: str, release_version: str
) -> None:
    git_service.tag_commit(commit=commit, tag=release_version)


def _push_tag_to_remote(git_service: GitService, release_version: str) -> None:
    git_service.push_to_remote(ref=release_version)


def _print_next_steps(version_number: str) -> None:
    tag_url = os.path.join(GxURL.RELEASES, "tag", version_number)
    click.secho(
        f"\nPlease wait for the build process and PyPI publishing to complete before moving to the `prep` cmd.",
        fg="green",
    )
    click.echo(f"Link to tag: {tag_url}")
    click.echo(f"Link to Azure build: {GxURL.AZURE_BUILDS}")
    click.echo(f"Link to PyPI page: {GxURL.PYPI_PAGE}")
