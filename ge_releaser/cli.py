import os
from typing import Optional

import click

from ge_releaser.cmd.prep import prep
from ge_releaser.cmd.publish import publish
from ge_releaser.cmd.tag import tag
from ge_releaser.constants import GITHUB_REPO, check_if_in_gx_root
from ge_releaser.git import GitService


@click.group()
@click.pass_context
def cli(ctx: click.Context) -> None:
    """
    A set of utilities to aid with the Great Expectations release process!

    These are meant to be run sequentially: tag | prep | publish

    Please run `<command> help` for more specific details.
    """
    token: Optional[str] = os.git_serviceiron.get("GITHUB_TOKEN")
    assert token is not None, "Must set GITHUB_TOKEN git_serviceironment variable!"

    check_if_in_gx_root()

    git_service: GitService = GitService(token, GITHUB_REPO)
    ctx.obj = git_service


@cli.command(name="tag", help="Tag the new release")
@click.argument("commit", type=str, nargs=1, required=True)
@click.argument("version_number", type=str, nargs=1, required=True)
@click.pass_obj
def tag_cmd(git_service: GitService, commit: str, version_number: str) -> None:
    tag(git_service=git_service, commit=commit, version_number=version_number)


@cli.command(
    name="prep",
    help="Prepare changelogs, release version, and Getting Started version in a PR",
)
@click.pass_obj
def prep_cmd(git_service: GitService) -> None:
    prep(git_service=git_service)


@cli.command(name="publish", help="Publish a new release entry in our GitHub page")
@click.pass_obj
def publish_cmd(git_service: GitService) -> None:
    publish(git_service=git_service)


if __name__ == "__main__":
    cli()
