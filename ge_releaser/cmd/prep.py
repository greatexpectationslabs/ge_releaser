import logging
import os
from typing import Final, Iterable, List, Tuple

import click
from github.PullRequest import PullRequest
from packaging import version

from ge_releaser.changelog import ChangelogEntry
from ge_releaser.constants import GxFile, GxURL
from ge_releaser.git import GitService

LOGGER: Final[logging.Logger] = logging.getLogger(__name__)


def prep(git: GitService) -> None:
    click.secho("[prep]", bold=True, fg="blue")

    last_version, release_version = _parse_versions(git)

    git.checkout_and_pull_trunk()

    release_branch: str = _create_and_checkout_release_branch(git, release_version)
    click.secho(" * Created a release branch (1/7)", fg="yellow")

    _update_deployment_version_file(release_version)
    click.secho(" * Updated deployment version file (2/7)", fg="yellow")

    _update_docs_component(last_version=last_version, release_version=release_version)
    click.secho(" * Updated version in docs data component (3/7)", fg="yellow")

    _update_docs_version_dropdown(
        last_version=last_version, release_version=release_version
    )
    click.secho(" * Updated version in docs version dropdown (4/7)", fg="yellow")

    _update_changelogs(
        git=git,
        last_version=last_version,
        release_version=release_version,
    )
    click.secho(" * Updated changelog (5/7)", fg="yellow")

    git.stage_all_and_commit("release_prep")
    click.secho(" * Committed changes (6/7)", fg="yellow")

    url: str = _create_pr(
        git=git,
        release_branch=release_branch,
        release_version=release_version,
    )
    click.secho(" * Opened prep PR (7/7)", fg="yellow")

    _print_next_steps(url, git)


def _parse_versions(
    git: GitService,
) -> Tuple[str, str]:
    tags_filter = "0." if git.trunk_is_0ver else "1."
    tags_generator = git.iter_recent_tags(prefix_filter=tags_filter, limit=2)
    release_version = version.parse(next(tags_generator))
    last_version = version.parse(next(tags_generator))

    LOGGER.info(f"{last_version=} {release_version=}")
    assert (
        release_version > last_version
    ), f"Version provided to command is not valid, {release_version} <= {last_version}"
    return str(last_version), str(release_version)


def _create_and_checkout_release_branch(git: GitService, release_version: str) -> str:
    branch_name: str = f"release-{release_version}"
    git.create_and_checkout_branch(branch_name)
    return branch_name


def _update_deployment_version_file(release_version: str) -> None:
    with open(GxFile.DEPLOYMENT_VERSION, "w") as f:
        f.write(f"{release_version.strip()}\n")


def _update_docs_component(last_version: str, release_version: str) -> None:
    """Updates the JSX file in our docs directory responsible for tracking GX and Python versions.

    It looks something like this:
    ```jsx
    export default {
      release_version: 'great_expectations, version 0.15.48',
      min_python: 'Python 3.7',
      max_python: 'Python 3.10'
    }
    ```
    """
    with open(GxFile.DOCS_DATA_COMPONENT) as f:
        contents = f.read()
    updated_contents = contents.replace(last_version, release_version)
    with open(GxFile.DOCS_DATA_COMPONENT, "w") as f:
        f.write(updated_contents)


def _update_docs_version_dropdown(last_version: str, release_version: str) -> None:
    """Updates the docusaurus config file responsible for display of the version dropdown.

    It looks something like this:
    ```js
    versions: {
        current: {
          label: '0.16.6',
          path: ''
        }
      }
    ```
    """
    with open(GxFile.DOCS_CONFIG) as f:
        contents = f.read()
    updated_contents = contents.replace(last_version, release_version)
    with open(GxFile.DOCS_CONFIG, "w") as f:
        f.write(updated_contents)


def _update_changelogs(
    git: GitService,
    last_version: str,
    release_version: str,
) -> None:
    relevant_prs = _collect_prs_since_last_release(git, last_version)

    changelog_entry = ChangelogEntry(relevant_prs)

    if git.trunk_is_0ver:
        changelog_entry.write(GxFile.CHANGELOG_MD_V0, last_version, release_version)
    else:
        changelog_entry.write(GxFile.CHANGELOG_MD_V1, last_version, release_version)


def _collect_prs_since_last_release(
    git: GitService,
    last_version: str,
) -> List[PullRequest]:
    # 20220923 - Chetan - Currently, this grabs all PRs from the last release until the moment of program execution.
    # This should be updated so the changelog generation stops once it hits the release commit.

    last_release = git.get_release_timestamp(last_version)

    merged_prs = git.get_merged_prs()
    recent_prs: List[PullRequest] = []

    # To ensure we don't accidently exit early, we set a threshold and wait to see a few old PRs before completing iteration
    counter = 0
    threshold = 5

    for pr in merged_prs:
        if counter >= threshold:
            break

        # Ignore closed PRs and any release-specific PRs
        if not pr.merged or "RELEASE" in pr.title:
            continue

        LOGGER.info(pr, pr.merged_at, counter)
        if pr.merged_at < last_release:
            counter += 1
        if pr.merged_at > last_release:
            recent_prs.append(pr)

    return recent_prs


def _create_pr(
    git: GitService,
    release_branch: str,
    release_version: str,
) -> str:
    git.push_branch_to_remote(release_branch, set_upstream=True)

    pr = git.create_pr(
        title=f"[RELEASE] {release_version}",
        body=f"release prep for {release_version}",
        head=release_branch,
    )

    return os.path.join(GxURL.PULL_REQUESTS, str(pr.number))


def _print_next_steps(url: str, git: GitService) -> None:
    click.secho(
        "\n[SUCCESS] Please review, approve, and merge PR before continuing to `publish` command",
        fg="green",
    )
    click.echo(f"Link to PR: {url}")
    if git.trunk_is_0ver:
        click.echo(
            f"TEMPORARY MANUAL STEP: Please copy over the new changes from the above PR into {GxFile.CHANGELOG_MD_V1} on develop."
        )
