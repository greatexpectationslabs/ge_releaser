import os
from typing import Optional

import click
import requests
from requests.models import HTTPError

from ge_releaser.constants import (
    GITHUB_REPO,
    RELEASER_LOCAL_VERSION,
    RELEASER_REMOTE_VERSION,
    REMOTE,
    TRUNK,
    GxFile,
)
from ge_releaser.git import GitService


def check_if_in_gx_root() -> None:
    for constant in GxFile:
        if not os.path.exists(constant):
            raise ValueError(
                f"Could not find '{constant}'; are you sure you're in the root of the OSS repo?"
            )


def check_if_using_latest_version() -> None:
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


def setup(ctx: click.Context) -> None:
    token: Optional[str] = os.environ.get("GITHUB_TOKEN")
    assert token is not None, "Must set GITHUB_TOKEN environment variable!"

    trunk_override: Optional[str] = os.environ.get("GX_RELEASE_TRUNK")
    if trunk_override and trunk_override != TRUNK:
        input(
            f"WARNING: GX_RELEASE_TRUNK is set to {trunk_override}. Press enter to continue. CTRL+C to exit."
        )

    check_if_in_gx_root()
    check_if_using_latest_version()

    git = GitService(
        github_token=token, repo_name=GITHUB_REPO, trunk=trunk_override or TRUNK, remote=REMOTE
    )
    git.verify_no_untracked_files()
    ctx.obj = git
