import os
from typing import Optional

import click

from ge_releaser.constants import GITHUB_REPO
from ge_releaser.git import GitEnvironment
from ge_releaser.prep import prep
from ge_releaser.release import release
from ge_releaser.tag import tag


@click.group()
@click.pass_context
def cli(ctx: click.Context) -> None:
    """
    A set of utilities to aid with the Great Expectations release process!

    These are meant to be run sequentially: prep | cut | tag | release

    Please run `<command> help` for more specific details.
    """
    token: Optional[str] = os.environ.get("GITHUB_TOKEN")
    assert token is not None, "Must set GITHUB_TOKEN environment variable!"

    env: GitEnvironment = GitEnvironment(token, GITHUB_REPO)
    ctx.obj = env


@cli.command(name="prep", help="Prepare changelog/release version PR")
@click.argument("version_number", type=str, nargs=1, required=False)
@click.option("--file", "file", type=click.Path(exists=True), required=False)
@click.pass_obj
def prep_cmd(
    env: GitEnvironment, version_number: Optional[str], file: Optional[str]
) -> None:
    assert bool(version_number) ^ bool(
        file
    ), "You must pass in a version number or point to a scheduler file!"
    prep(env, version_number, file)


@cli.command(name="tag", help="Tag the new release")
@click.pass_obj
def tag_cmd(env: GitEnvironment) -> None:
    tag(env)


@cli.command(name="release", help="Create a new release entry in our GitHub page")
@click.pass_obj
def release_cmd(env: GitEnvironment) -> None:
    release(env)


if __name__ == "__main__":
    cli()
