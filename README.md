### ge_releaser

A CLI tool built to streamline the process of cutting releases each week in the OSS repository.

---

#### Installation
```bash
git clone git@github.com:superconductive/ge_releaser.git
pip install -e .
```

You'll also need to set up a `GITHUB_TOKEN` environment variable to get past
the service's rate limiting.
  1. Follow the steps [here](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token) to create a token.
  2. Save that token with `export GITHUB_TOKEN=...`

Make sure you enable the appropriate read/write privledges when setting up your token (PR's, tags, releases, etc).

---

#### Usage
```bash
# Commands are meant to be run sequentially
ge_releaser prep 0.15.2  # Modify changelogs and open a PR.
ge_releaser cut          # Update main and trigger build process
ge_releaser tag          # Tag the appropriate commit
ge_releaser release      # Create a new GitHub release page
```

The tool is designed to do pretty much EVERYTHING for you. Do not run isolated `git` commands (unless resolving merge conflicts).
