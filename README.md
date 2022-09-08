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
These commands are to be executed in Great Expectations development directory (be sure to check out the `develop` branch).

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
  - Create a [personal access GitHub token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token), unless you already have one.
  - Authorize it for use with [SAML SSO](https://docs.github.com/en/enterprise-cloud@latest/authentication/authenticating-with-saml-single-sign-on/authorizing-a-personal-access-token-for-use-with-saml-single-sign-on), unless this has already been done previously.
  - Save that token with `export GITHUB_TOKEN=...`.
- Test the release candidate
  - Message #topic-great_expectations @channel to ask team members to hold off on merging to `develop`
  - Look for a release PR on github. It will be named `[RELEASE] <RELEASE_NUMBER>`, eg `[RELEASE] 0.15.18`.  Please note that oftentimes this release PR is created automatically hours ahead of the present steps being carried out.  This means that the working branch of the release PR may be out of date.  In this case, when `develop` is reliably frozen, update this working branch.
    - If none is present run: `ge_releaser prep <release_version>`
  - Before running tests on the release candidate you will want to check that the last automated build is passing. 
    - If it is not, testing the release will likely not go through successfully. 
    - The slack channel #notifications-great_expectations surfaces failures.
    - The automated pipeline can be viewed on our [pipeline page](https://dev.azure.com/great-expectations/great_expectations/_build?definitionId=1). Search for lines like `Scheduled for ... develop`
  - If there were errors or if you need to add any PRs to the build you will need to update the release notes.
    - The release notes are at `/docs/changelog.md` and `/docs_rtd/changelog.rst`. The `.rst` file is a legacy file but needs to be kept up to date for the time being.
    - These release note lines are commit messages. You can run `git log` if you want to add new ones. The files are organized by type, then chronologically. If there is no type on a commit message, prepend `[MAINTENANCE]`
  - Make sure that there is an entry in `release_schedule.json` for the next release.
  - Approve the auto-generated PR.
  - Open Azure and run the `great_expectations` pipeline fully (this will be automated in the future). Here is a [video description of this step](https://www.loom.com/share/2da11fadc7df4fbb80c55384b7729c24).
  - Merge the auto-generated PR after all tests pass.
- Run `ge_releaser tag` and wait for the azure pipeline to finish
  - Once the `ge_releaser tag` build has finished with all tests passing, you can allow merges to develop while completing the remaining steps. This is done my messaging the #topic-great_expectations channel.
- Run `ge_releaser release`
- Send a draft message (to be reviewed by the team) to #topic-great_expectations, with the message that will be sent in the community Slack.
  - When you call out contributors, use there slack handle: @\<slack username\>
  - If no slack handle is present go to github and look at their user profile: https://github.com/<username> and then use "Real name (\<github username\>)":
  - If they have no real name, use their github handle: "\<github username\>"
- Send the reviewed message to the community Slack channel #announcements.
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
- Make sure that there is another entry in `release_schedule.json` for the next release.
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
