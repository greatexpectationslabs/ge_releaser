# ge_releaser

A CLI tool built to streamline the process of cutting releases each week in the OSS repository.

---

## Installation
```bash
# Preferably run all this in a venv
git clone git@github.com:superconductive/ge_releaser.git
cd ge_releaser
pip install -e .
```

## Commands
```bash
# Commands are meant to be run sequentially
ge_releaser prep 0.15.2  # Modify changelogs and open a PR.
ge_releaser tag          # Tag the appropriate commit and trigger the build process
ge_releaser release      # Create a new GitHub release page
```

The tool is designed to do pretty much EVERYTHING for you. Do not run isolated `git` commands (unless resolving merge conflicts).

---

## Walkthrough

`ge_releaser` acts as an abstraction on top of our standard manual release process. While the following steps should get you creating releases with ease, it is also important to understand what is happening under the hood. For each of the primary commands that `ge_releaser` offers, the individual manual steps taken by the machine are noted below. Although you shouldn't have to use them, it may be handy if debugging is required.

### CLI Process
- Install and setup the tool
  - Install the tool using the above instructions.
  - Create a [personal access GitHub token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token).
  - Authorize it for use with [SAML SSO](https://docs.github.com/en/enterprise-cloud@latest/authentication/authenticating-with-saml-single-sign-on/authorizing-a-personal-access-token-for-use-with-saml-single-sign-on).
  - Save that token with `export GITHUB_TOKEN=...`.
- NOTE: this step is automated so check github for a PR on Thurs morning. If not: Run `ge_releaser prep <release_version>`.
  - Make sure that there are at least two entries in `release_schedule.json` - one for the next release, and one that will be used as a template after the line for the next release is removed.
  - Message #topic-great_expectations @channel to ask team members to hold off on merging to `develop`
  - Approve the auto-generated PR and merge it.
  - Open Azure and run the `great_expectations` pipeline fully (this will be automated in the future)
- Run `ge_releaser tag` and wait for the build to finish
  - Once the `ge_releaser tag` build has started, you can allow merges to develop while completing the remaining steps.
- Run `ge_releaser release`
- Send a draft message (to be reviewed by the team) to #topic-great_expectations, with the message that will be sent in the community Slack.
- Send the reviewed meesage to the community Slack channel #announcements.
- Request emoji signal boosting from the team in private Slack channel #topic-great_expectations.

### Manual Process

#### prep:
- Pull remote changes into your local `develop`.
  - Command: `git checkout develop; git pull origin/develop`
- Create a new branch from `develop` called `release-X.Y.Z`.
  - Command: `git checkout -b release-X.Y.Z`
- Update the version in `great_expectations/deployment_version`.
- Update the version in `docs/tutorials/getting_started/tutorial_version_snippet.mdx`.
- Add a new entry to `docs/changelog.md` and `docs_rtd/changelog.rst`.
  - Ensure that lines are ordered by: `[BREAKING] | [FEATURE] | [BUGFIX] | [DOCS] | [MAINTENANCE]`
  - Ensure that each line has a reference to its corresponding PR.
  - If coming from an external contributor, make sure the line ends in `(thanks @<contributor_id>)`.
- Make sure that there are at least two entries in `release_schedule.json` - one for the next release, and one that will be used as a template after the line for the next release is removed.
- Commit these three files and create a PR against `develop`.
  - Command: `git add great_expectations; git commit -m "release prep"; git push`
- Receive approval and merge the PR.
  - You will have to wait for Azure CI/CD to run its checks.
  - Open azure and run the `great_expectations` pipeline fully (this will be automated in the future)

#### tag:
- Create a tag for the new release.
  - Command: `git tag -a <release_version> -m "<release_version>"; git push origin <release_version>`
- Wait for Azure to finish its checks.
  - A successful run with automatically publish the new version to PyPI.

#### release:
- Create a release entry in GitHub.

### post-release:
- Send a draft message (to be reviewed by the team) to #topic-great_expectations, with the message that will be sent in the community Slack.
- Send the reviewed meesage to the community Slack channel #announcements.
- Request emoji signal boosting from the team in private Slack channel #topic-great_expectations.
