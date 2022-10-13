from typing import List

import setuptools


def get_requirements() -> List[str]:
    with open("requirements.txt") as f:
        requirements = f.read().splitlines()
    return requirements


setuptools.setup(
    name="ge_releaser",
    version="0.1.0",
    install_requires=get_requirements(),
    entry_points="""
      [console_scripts]
      ge_releaser=ge_releaser.cli:cli
    """,
    packages=["ge_releaser"],
)
