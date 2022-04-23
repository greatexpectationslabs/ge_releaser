import os
from typing import Optional

import click

from ge_releaser.cut import cut
from ge_releaser.env import Environment
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

    env: Environment = Environment(token)
    ctx.obj = env


@cli.command(name="prep", help="Prepare changelog/release version PR")
@click.argument("version_number", type=str, nargs=1)
@click.pass_obj
def prep_cmd(env: Environment, version_number: str) -> None:
    prep(env, version_number)


@cli.command(
    name="cut", help="Trigger the build process to automate publishing to PyPI"
)
@click.pass_obj
def cut_cmd(env: Environment) -> None:
    cut(env)


@cli.command(name="tag", help="Tag the new release")
@click.pass_obj
def tag_cmd(env: Environment) -> None:
    tag(env)


@cli.command(name="release", help="Create a new release entry in our GitHub page")
@click.pass_obj
def release_cmd(env: Environment) -> None:
    release(env)


if __name__ == "__main__":
    cli()
