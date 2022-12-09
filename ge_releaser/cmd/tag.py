import os

import click
import git

from ge_releaser.constants import GxURL
from ge_releaser.git import GitEnvironment


def tag(env: GitEnvironment, commit: str, version_number: str) -> None:
    click.secho("[tag]", bold=True, fg="blue")

    _tag_release_commit(env.git_repo, commit, version_number)
    click.secho(f" * Tagged commit '{commit}' on develop (1/2)", fg="yellow")

    _push_tag_to_remote(env.git_repo, version_number)
    click.secho(" * Pushed tag to remote (2/2)", fg="yellow")

    _print_next_steps(version_number)


def _tag_release_commit(git_repo: git.Repo, commit: str, release_version: str) -> None:
    if "develop" not in git_repo.git.branch("--contains", commit):
        raise ValueError("Selected commit is not a part of the 'develop' branch!")

    git_repo.git.checkout(commit)
    git_repo.git.tag("-a", release_version, "-m", f'"{release_version}"')


def _push_tag_to_remote(git_repo: git.Repo, release_version: str) -> None:
    git_repo.git.push("origin", release_version)


def _print_next_steps(version_number: str) -> None:
    tag_url: str = os.path.join(GxURL.RELEASES, "tag", version_number)
    click.secho(
        f"\nPlease wait for the build process and PyPI publishing to complete before moving to the `prep` cmd.",
        fg="green",
    )
    click.echo(f"Link to tag: {tag_url}")
    click.echo(f"Link to Azure build: {GxURL.AZURE_BUILDS}")
    click.echo(f"Link to PyPI page: {GxURL.PYPI_PAGE}")
