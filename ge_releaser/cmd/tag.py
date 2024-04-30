import os

import click
from packaging import version

from ge_releaser.constants import GxURL
from ge_releaser.git import GitService


def tag(
    git: GitService, commit: str, version_number: str, is_stable_release: bool
) -> None:
    _check_version_validity(
        version_number=version_number, is_stable_release=is_stable_release
    )
    click.secho("[tag]", bold=True, fg="blue")

    _tag_release_commit(git, commit, version_number)
    click.secho(f" * Tagged commit '{commit}' on {git.trunk} (1/2)", fg="yellow")

    git.push_branch_to_remote(branch=version_number, set_upstream=False)
    click.secho(" * Pushed tag to remote (2/2)", fg="yellow")

    _print_next_steps(version_number=version_number)


def _check_version_validity(version_number: str, is_stable_release: bool) -> None:
    v = version.parse(version_number)

    if is_stable_release and v.is_prerelease:
        raise ValueError(
            "Passed in --stable flag but provided an invalid version with a pre-release suffix"
        )

    if not is_stable_release and not v.is_prerelease:
        raise ValueError(
            "Passed in a stable version but did not turn on the --stable flag"
        )


def _tag_release_commit(git: GitService, commit: str, release_version: str) -> None:
    if not git.check_if_commit_is_part_of_trunk(commit):
        raise ValueError(
            f"Selected commit {commit} is not a part of the '{git.trunk}' branch!"
        )

    git.tag_commit(commit=commit, version=release_version)


def _print_next_steps(version_number: str) -> None:
    tag_url = os.path.join(GxURL.RELEASES, "tag", version_number)

    msg = ("Please start a thread in #gx-platform-release about the release and update the thread as the release progresses. "
           "Make sure to wait for the build process and PyPI publishing to complete before moving to the `prep` cmd.")

    click.secho(f"\n{msg}", fg="green")
    click.echo(f"Link to tag: {tag_url}")
    # this is here to make it easier to copy-paste the link
    click.echo(f"Link to Github Actions build: {GxURL.GITHUB_ACTIONS_BUILD}")
    click.echo(f"Link to PyPI page: {GxURL.PYPI_PAGE}")
