import os

# Constants used in business logic
DEPLOYMENT_VERSION: str = "great_expectations/deployment_version"
CHANGELOG_MD: str = "docs/changelog.md"
CHANGELOG_RST: str = "docs_rtd/changelog.rst"
TEAMS_YAML: str = ".github/teams.yml"

# Misc constants
GITHUB_REPO: str = "great-expectations/great_expectations"
AZURE_BUILDS: str = (
    "https://dev.azure.com/great-expectations/great_expectations/_build?definitionId=1"
)
PYPI_PAGE: str = "https://pypi.org/project/great-expectations/#history"
RELEASES: str = "https://github.com/great-expectations/great_expectations/releases"


def all_constants_are_valid() -> bool:
    for constant in (DEPLOYMENT_VERSION, CHANGELOG_MD, CHANGELOG_RST, TEAMS_YAML):
        exists: bool = os.path.exists(constant)
        if not exists:
            print(f"Could not find {constant}!")
            return False
    return True
