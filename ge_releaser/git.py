import git
import github
from github.Organization import Organization
from github.Repository import Repository


class GitEnvironment:
    def __init__(self, github_token: str, repo_name: str) -> None:
        self.git_repo: git.Repo = git.Repo()

        gh: github.Github = github.Github(github_token)
        self.github_repo: Repository = gh.get_repo(repo_name)
        self.github_org: Organization = gh.get_organization(login="Superconductive")
