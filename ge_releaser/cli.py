import os
from typing import Optional

import click

from ge_releaser.cmd.prep import prep
from ge_releaser.cmd.publish import publish
from ge_releaser.cmd.tag import tag
from ge_releaser.constants import GITHUB_REPO, check_if_in_gx_root
from ge_releaser.git import GitEnvironment


@click.group()
@click.pass_context
def cli(ctx: click.Context) -> None:
    """
    A set of utilities to aid with the Great Expectations release process!

    These are meant to be run sequentially: tag | prep | publish

    Please run `<command> help` for more specific details.
    """
    token: Optional[str] = os.environ.get("GITHUB_TOKEN")
    assert token is not None, "Must set GITHUB_TOKEN environment variable!"

    check_if_in_gx_root()

    env: GitEnvironment = GitEnvironment(token, GITHUB_REPO)
    ctx.obj = env


@cli.command(name="tag", help="Tag the new release")
@click.argument("commit", type=str, nargs=1, required=True)
@click.argument("version_number", type=str, nargs=1, required=True)
@click.pass_obj
def tag_cmd(env: GitEnvironment, commit: str, version_number: str) -> None:
    tag(env=env, commit=commit, version_number=version_number)


@cli.command(
    name="prep",
    help="Prepare changelogs, release version, and Getting Started version in a PR",
)
@click.pass_obj
def prep_cmd(env: GitEnvironment) -> None:
    prep(env=env)


@cli.command(name="publish", help="Publish a new release entry in our GitHub page")
@click.pass_obj
def publish_cmd(env: GitEnvironment) -> None:
    publish(env=env)


if __name__ == "__main__":
    cli()
