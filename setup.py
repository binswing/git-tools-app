from setuptools import setup, find_packages

setup(
    name="git-ai",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["requests", "pygame"],
    entry_points={
        "console_scripts": [
            "git-ai=git_ai.cli:main",
        ],
    },
)