import os
from typing import List

DEPLOYMENT_VERSION: str = "great_expectations/deployment_version"
CHANGELOG_MD: str = "docs/changelog.md"
CHANGELOG_RST: str = "docs_rtd/changelog.rst"
TEAMS: str = ".github/teams.yml"

GITHUB_REPO: str = "great-expectations/great_expectations"
AZURE_BUILDS: str = f"https://dev.azure.com/{GITHUB_REPO}/_build?definitionId=1"
PYPI_PAGE: str = "https://pypi.org/project/great-expectations/#history"
BASE_URL: str = f"https://github.com/{GITHUB_REPO}"
RELEASES: str = f"{BASE_URL}/releases"
PULL_REQUESTS: str = f"{BASE_URL}/pull"

FILESYSTEM_CONSTANTS: List[str] = [
    DEPLOYMENT_VERSION,
    CHANGELOG_MD,
    CHANGELOG_RST,
    TEAMS,
]

for constant in FILESYSTEM_CONSTANTS:
    if not os.path.exists(constant):
        raise ValueError(
            f"Could not find '{constant}'; are you sure you're in the root of the OSS repo?"
        )
