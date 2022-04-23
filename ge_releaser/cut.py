import sys
import click
import git

from ge_releaser.constants import AZURE_BUILDS, PYPI_PAGE

def update_local_branches_and_switch_to_main(git_repo: git.Repo) -> None:
    git_repo.git.fetch("--all")
    git_repo.git.checkout("main")
    git_repo.git.pull("origin", "main")


def merge_develop(git_repo: git.Repo) -> None:
    git_repo.git.merge("origin/develop")

def cut_release(git_repo: git.Repo) -> None:
    confirmation: str = input("\nAre you sure you want to cut the release [y/n]: ")
    if not confirmation.lower().startswith("y"):
        sys.exit(1)

    git_repo.git.push("origin", "main")


def cut(git_repo: git.Repo):
    click.secho("[cut]", bold=True, fg="blue")

    update_local_branches_and_switch_to_main(git_repo)
    click.secho(" * Pulled latest main (1/3)", fg="yellow")

    merge_develop(git_repo)
    click.secho(" * Merged develop (2/3)", fg="yellow")

    cut_release(git_repo)
    click.secho(" * Cut release (3/3)", fg="yellow")

    click.secho(
        f"\n[SUCCESS] Please wait for the build process and PyPI publishing to complete before moving to the `tag` cmd.",
        fg="green",
    )
    click.echo(f"Link to Azure build: {AZURE_BUILDS}")
    click.echo(f"Link to PyPI page: {PYPI_PAGE}")
