import os
from typing import Optional

import click
import requests
from requests.models import HTTPError

from ge_releaser.cmd.prep import prep
from ge_releaser.cmd.publish import publish
from ge_releaser.cmd.tag import tag
from ge_releaser.constants import (
    GITHUB_REPO,
    RELEASER_LOCAL_VERSION,
    RELEASER_REMOTE_VERSION,
    check_if_in_gx_root,
)
from ge_releaser.git import GitEnvironment


def check_if_using_latest_version():
    current_version = _get_current_version()
    latest_version = _get_latest_version()
    if current_version != latest_version:
        raise ValueError(
            f"Your version of `ge_releaser` is outdated (local: {current_version}, remote: {latest_version}).\nPlease pull down latest changes before continuing."
        )


def _get_current_version() -> str:
    with open(RELEASER_LOCAL_VERSION) as f:
        return f.read().strip()


def _get_latest_version() -> str:
    response = requests.get(RELEASER_REMOTE_VERSION)
    try:
        response.raise_for_status()
    except HTTPError as e:
        raise ValueError("Could not access remote version of `ge_releaser`") from e
    return response.text.strip()


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
    check_if_using_latest_version()

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
