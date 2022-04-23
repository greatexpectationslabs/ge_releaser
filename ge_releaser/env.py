import os
from typing import List

import git
import github
from github.Organization import Organization
from github.Repository import Repository


class Environment:

    # Constants used in business logic
    DEPLOYMENT_VERSION: str = "great_expectations/deployment_version"
    CHANGELOG_MD: str = "docs/changelog.md"
    CHANGELOG_RST: str = "docs_rtd/changelog.rst"

    # Misc constants
    GITHUB_REPO: str = "great-expectations/great_expectations"
    AZURE_BUILDS: str = "https://dev.azure.com/great-expectations/great_expectations/_build?definitionId=1"
    PYPI_PAGE: str = "https://pypi.org/project/great-expectations/#history"
    RELEASES: str = "https://github.com/great-expectations/great_expectations/releases"

    def __init__(self, token: str) -> None:
        assert (
            Environment._all_constants_are_valid()
        ), "One or more constants not found! Please ensure you're in the root of the OSS repo."
        self.git_repo: git.Repo = git.Repo()
        gh: github.Github = github.Github(token)
        self.github_repo: Repository = gh.get_repo(Environment.GITHUB_REPO)
        self.github_org: Organization = gh.get_organization(login="Superconductive")

    @staticmethod
    def _all_constants_are_valid() -> bool:
        to_check: List[str] = [
            Environment.DEPLOYMENT_VERSION,
            Environment.CHANGELOG_MD,
            Environment.CHANGELOG_RST,
        ]

        for constant in to_check:
            exists: bool = os.path.exists(constant)
            if not exists:
                print(f"Could not find {constant}!")
                return False
        return True
