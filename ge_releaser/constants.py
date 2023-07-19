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
    AZURE_BUILDS = f"https://dev.azure.com/{GITHUB_REPO}/_build?definitionId=1"
    PYPI_PAGE = "https://pypi.org/project/great-expectations/#history"
    BASE_URL = f"https://github.com/{GITHUB_REPO}"
    RELEASES = f"{BASE_URL}/releases"
    PULL_REQUESTS = f"{BASE_URL}/pull"


class GxFile(str, enum.Enum):
    DEPLOYMENT_VERSION = "great_expectations/deployment_version"
    CHANGELOG_MD = "docs/docusaurus/docs/changelog.md"
    CHANGELOG_RST = "docs_rtd/changelog.rst"
    TEAMS = ".github/teams.yml"
    DOCS_DATA_COMPONENT = "docs/docusaurus/docs/components/_data.jsx"
    DOCS_CONFIG = "docs/docusaurus/docusaurus.config.js"


FILES_TO_COMMIT = (
    GxFile.CHANGELOG_MD,
    GxFile.DOCS_DATA_COMPONENT,
    GxFile.DOCS_CONFIG,
    GxFile.CHANGELOG_RST,
    GxFile.DEPLOYMENT_VERSION,
)
