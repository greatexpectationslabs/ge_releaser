import os
from typing import Optional

import click

from ge_releaser.cmd.prep import prep
from ge_releaser.cmd.publish import publish
from ge_releaser.cmd.tag import tag
from ge_releaser.constants import GITHUB_REPO, REMOTE, TRUNK, GxFile
from ge_releaser.git import GitService


def _check_if_in_gx_root() -> None:
    for constant in GxFile:
        if not os.path.exists(constant):
            raise ValueError(
                f"Could not find '{constant}'; are you sure you're in the root of the OSS repo?"
            )


def setup(ctx: click.Context) -> None:
    token: Optional[str] = os.environ.get("GITHUB_TOKEN")
    assert token is not None, "Must set GITHUB_TOKEN environment variable!"

    _check_if_in_gx_root()

    git = GitService(
        github_token=token, repo_name=GITHUB_REPO, trunk=TRUNK, remote=REMOTE
    )
    ctx.obj = git


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
@click.pass_obj
def tag_cmd(git: GitService, commit: str, version_number: str) -> None:
    tag(git=git, commit=commit, version_number=version_number)


@cli.command(
    name="prep",
    help="Prepare changelogs, release version, and Getting Started version in a PR",
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
