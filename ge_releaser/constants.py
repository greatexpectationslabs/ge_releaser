import enum
import os

GITHUB_REPO: str = "great-expectations/great_expectations"


class GxURL(str, enum.Enum):
    AZURE_BUILDS = f"https://dev.azure.com/{GITHUB_REPO}/_build?definitionId=1"
    PYPI_PAGE = "https://pypi.org/project/great-expectations/#history"
    BASE_URL = f"https://github.com/{GITHUB_REPO}"
    RELEASES = f"{BASE_URL}/releases"
    PULL_REQUESTS = f"{BASE_URL}/pull"


class GxFile(str, enum.Enum):
    DEPLOYMENT_VERSION = "great_expectations/deployment_version"
    CHANGELOG_MD = "docs/changelog.md"
    CHANGELOG_RST = "docs_rtd/changelog.rst"
    TEAMS = ".github/teams.yml"
    GETTING_STARTED_VERSION = (
        "docs/tutorials/getting_started/tutorial_version_snippet.mdx"
    )


def check_if_in_gx_root():
    for constant in GxFile:
        if not os.path.exists(constant):
            raise ValueError(
                f"Could not find '{constant}'; are you sure you're in the root of the OSS repo?"
            )
