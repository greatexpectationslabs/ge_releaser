from typing import cast

import git
from packaging import version

from ge_releaser.constants import GxFile


def checkout_and_update_develop(git_repo: git.Repo) -> None:
    git_repo.git.checkout("develop")
    git_repo.git.pull("origin", "develop")


def parse_deployment_version_file() -> version.Version:
    with open(GxFile.DEPLOYMENT_VERSION) as f:
        contents: str = str(f.read()).strip()
        current_version = cast(version.Version, version.parse(contents))

    return current_version
