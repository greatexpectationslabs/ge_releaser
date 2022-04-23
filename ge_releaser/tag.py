from typing import Union

import click
import git
from packaging import version

from ge_releaser.constants import DEPLOYMENT_VERSION


def parse_release_version() -> str:
    with open(DEPLOYMENT_VERSION) as f:
        contents: str = str(f.read()).strip()

    release_version: Union[version.Version, version.LegacyVersion] = version.parse(
        contents
    )
    return str(release_version)


def tag_latest_main(git_repo: git.Repo, release_version: str) -> None:
    git_repo.git.checkout("main")
    git_repo.git.tag("-a", release_version, "-m", f'"{release_version}"')


def push_tag_to_remote(git_repo: git.Repo, release_version: str) -> None:
    git_repo.git.push("origin", release_version)


def update_develop_with_tag(git_repo: git.Repo) -> None:
    git_repo.git.checkout("develop")
    git_repo.git.pull("origin", "develop")
    git_repo.git.merge("main")


def tag(git_repo: git.Repo) -> None:
    click.secho("[tag]", bold=True, fg="blue")

    release_version: str = parse_release_version()

    tag_latest_main(git_repo, release_version)
    click.secho(" * Tagged latest commit on main (1/3)", fg="yellow")

    push_tag_to_remote(git_repo, release_version)
    click.secho(" * Pushed tag to remote (2/3)", fg="yellow")

    update_develop_with_tag(git_repo)
    click.secho(" * Updated develop with new tag (3/3)", fg="yellow")

    click.secho(
        f"\n[SUCCESS] Please ensure your tag is accurate before moving to the `release` command",
        fg="green",
    )
    tag_url: str = f"https://github.com/great-expectations/great_expectations/releases/tag/{release_version}"
    click.echo(f"Link to tag: {tag_url}")
