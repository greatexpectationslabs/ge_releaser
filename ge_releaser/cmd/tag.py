import os

import click

from ge_releaser.constants import GxURL
from ge_releaser.git import GitService


def tag(git: GitService, commit: str, version_number: str) -> None:
    click.secho("[tag]", bold=True, fg="blue")

    _tag_release_commit(git, commit, version_number)
    click.secho(f" * Tagged commit '{commit}' on develop (1/2)", fg="yellow")

    git.push_branch_to_remote(branch=version_number, set_upstream=False)
    click.secho(" * Pushed tag to remote (2/2)", fg="yellow")

    _print_next_steps(version_number)


def _tag_release_commit(git: GitService, commit: str, release_version: str) -> None:
    if not git.check_if_commit_is_part_of_trunk(commit):
        raise ValueError(
            f"Selected commit {commit} is not a part of the 'develop' branch!"
        )

    git.tag_commit(commit=commit, version=release_version)


def _print_next_steps(version_number: str) -> None:
    tag_url = os.path.join(GxURL.RELEASES, "tag", version_number)
    click.secho(
        "\nPlease wait for the build process and PyPI publishing to complete before moving to the `prep` cmd.",
        fg="green",
    )
    click.echo(f"Link to tag: {tag_url}")
    # this is here to make it easier to copy-paste the link
    click.echo(f"Link to Github Actions build: {GxURL.GITHUB_ACTIONS_BUILD}")
    click.echo(f"Link to PyPI page: {GxURL.PYPI_PAGE}")
