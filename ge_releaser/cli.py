import os
from typing import Optional, Tuple

import click
import git
import github
from github.Repository import Repository

from ge_releaser.constants import GITHUB_REPO, all_constants_are_valid
from ge_releaser.cut import cut
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
    assert (
        all_constants_are_valid()
    ), "Please ensure that you are in the root of the Great Expectations OSS repo before using this tool!"

    token: Optional[str] = os.environ.get("GITHUB_TOKEN")
    assert token is not None, "Must set GITHUB_TOKEN environment variable!"

    git_repo: git.Repo = git.Repo()
    gh: github.Github = github.Github(token)
    github_repo: Repository = gh.get_repo(GITHUB_REPO)

    ctx.obj = (git_repo, github_repo)


@cli.command(name="prep", help="Prepare changelog/release version PR")
@click.argument("version_number", type=str, nargs=1)
@click.pass_obj
def prep_cmd(repos: Tuple[git.Repo, Repository], version_number: str) -> None:
    prep(repos[0], repos[1], version_number)


@cli.command(
    name="cut", help="Trigger the build process to automate publishing to PyPI"
)
@click.pass_obj
def cut_cmd(repos: Tuple[git.Repo, Repository]) -> None:
    cut(repos[0])


@cli.command(name="tag", help="Tag the new release")
@click.pass_obj
def tag_cmd(repos: Tuple[git.Repo, Repository]) -> None:
    tag(repos[0])


@cli.command(name="release", help="Create a new release entry in our GitHub page")
@click.pass_obj
def release_cmd(repos: Tuple[git.Repo, Repository]) -> None:
    release(repos[1])


if __name__ == "__main__":
    cli()
