from typing import List, cast

import click
from packaging import version

from ge_releaser.constants import GxFile, GxURL
from ge_releaser.git import GitService


def publish(git_service: GitService) -> None:
    click.secho("[publish]", bold=True, fg="blue")

    release_version = str(_parse_deployment_version_file())

    _create_release(git_service=git_service, release_version=release_version)

    _print_next_steps()

def _parse_deployment_version_file() -> version.Version:
    with open(GxFile.DEPLOYMENT_VERSION) as f:
        contents: str = str(f.read()).strip()
        current_version = cast(version.Version, version.parse(contents))

    return current_version


def _create_release(git_service: GitService, release_version: str) -> None:
    release_notes = _gather_release_notes(release_version)
    message = "".join(line for line in release_notes)

    git_service.create_git_release(release_version=release_version, message=message)


def _gather_release_notes(release_version: str) -> List[str]:
    with open(GxFile.CHANGELOG_MD, "r") as f:
        contents: List[str] = f.readlines()

    start: int = 0
    end: int = 0
    for i, line in enumerate(contents):
        if release_version in line:
            start = i + 1
        if start != 0 and len(line.strip()) == 0:
            end = i
            break

    return contents[start:end]


def _print_next_steps() -> None:
    click.secho(" * Created release page (1/1)", fg="yellow")

    click.secho(
        f"\n[SUCCESS] Please review and publish your release. Congratulations, you've finished the release process :)",
        fg="green",
    )
    click.echo(f"Link to releases: {GxURL.RELEASES}")
