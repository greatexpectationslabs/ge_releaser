from typing import List

import setuptools


def get_version() -> str:
    with open("VERSION") as f:
        version = f.read().strip()
    return version


def get_requirements() -> List[str]:
    with open("requirements.txt") as f:
        requirements = f.read().splitlines()
    return requirements


setuptools.setup(
    name="ge_releaser",
    version=get_version(),
    install_requires=get_requirements(),
    python_requires=">=3.8",
    entry_points="""
      [console_scripts]
      ge_releaser=ge_releaser.cli:cli
    """,
    packages=["ge_releaser"],
)
