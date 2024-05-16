import enum
import pathlib

RELEASER_LOCAL_VERSION = str(
    pathlib.Path(__file__).parent.parent.joinpath("VERSION").resolve()
)
RELEASER_REMOTE_VERSION = (
    "https://raw.githubusercontent.com/greatexpectationslabs/ge_releaser/main/VERSION"
)
TRUNK = "develop"
REMOTE = "origin"
GITHUB_REPO = "great-expectations/great_expectations"


class GxURL(str, enum.Enum):
    GITHUB_ACTIONS_BUILD = (
        f"https://github.com/{GITHUB_REPO}/actions/workflows/ci.yml?query=event%3Apush"
    )
    PYPI_PAGE = "https://pypi.org/project/great-expectations/#history"
    BASE_URL = f"https://github.com/{GITHUB_REPO}"
    RELEASES = f"{BASE_URL}/releases"
    PULL_REQUESTS = f"{BASE_URL}/pull"


class GxFile(str, enum.Enum):
    DEPLOYMENT_VERSION = "great_expectations/deployment_version"
    CHANGELOG_MD_V1 = "docs/docusaurus/docs/oss/changelog.md"
    CHANGELOG_MD_V0 = "docs/docusaurus/docs/changelog.md"
    TEAMS = ".github/teams.yml"
    DOCS_DATA_COMPONENT = "docs/docusaurus/docs/components/_data.jsx"
    DOCS_CONFIG = "docs/docusaurus/docusaurus.config.js"
