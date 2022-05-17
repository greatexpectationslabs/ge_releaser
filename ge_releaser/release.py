from typing import List

import click
from github.Repository import Repository

from ge_releaser.constants import CHANGELOG_MD, RELEASES
from ge_releaser.git import GitEnvironment
from ge_releaser.util import parse_deployment_version_file


def release(env: GitEnvironment) -> None:
    click.secho("[release]", bold=True, fg="blue")

    release_version: str = str(parse_deployment_version_file())

    _create_release(env.github_repo, release_version, draft=False)
    click.secho(" * Created release page (1/1)", fg="yellow")

    click.secho(
        f"\n[SUCCESS] Please review and publish your release. Congratulations, you've finished the release process :)",
        fg="green",
    )
    click.echo(f"Link to releases: {RELEASES}")


def _create_release(github_repo: Repository, release_version: str, draft: bool) -> None:
    release_notes: List[str] = _gather_release_notes(release_version)
    message: str = "".join(line for line in release_notes)

    github_repo.create_git_release(
        tag=release_version, name=release_version, message=message, draft=draft
    )


def _gather_release_notes(release_version: str) -> List[str]:
    with open(CHANGELOG_MD, "r") as f:
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
