import logging
import os
from typing import Final

import click

from ge_releaser.cmd.prep import prep
from ge_releaser.cmd.publish import publish
from ge_releaser.cmd.tag import tag
from ge_releaser.git import GitService
from ge_releaser.utils import setup

LOG_LEVEL_NAME: Final[str] = os.environ.get("GE_RELEASE_LOG_LEVEL", "WARNING")
LOG_LEVEL: Final[int] = logging.getLevelName(LOG_LEVEL_NAME.upper())

logging.basicConfig(level=LOG_LEVEL)


@click.group()
@click.pass_context
def cli(ctx: click.Context) -> None:
    """
    A set of utilities to aid with the Great Expectations release process!

    These are meant to be run sequentially: tag | prep | publish

    Please run `<command> help` for more specific details.
    """
    setup(ctx)


@cli.command(name="tag", help="Tag the new release")
@click.argument("commit", type=str, nargs=1, required=True)
@click.argument("version_number", type=str, nargs=1, required=True)
@click.option("--stable", "is_stable_release", default=False, is_flag=True)
@click.pass_obj
def tag_cmd(
    git: GitService, commit: str, version_number: str, is_stable_release: bool
) -> None:
    tag(
        git=git,
        commit=commit,
        version_number=version_number,
        is_stable_release=is_stable_release,
    )


@cli.command(
    name="prep",
    help="Prepare changelog, release version, and Getting Started version in a PR",
)
@click.pass_obj
def prep_cmd(git: GitService) -> None:
    prep(git=git)


@cli.command(name="publish", help="Publish a new release entry in our GitHub page")
@click.pass_obj
def publish_cmd(git: GitService) -> None:
    publish(git=git)


if __name__ == "__main__":
    cli()
