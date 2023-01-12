from setuptools import setup
import os

VERSION = "0.1a2"


def get_long_description():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()


setup(
    name="datasette-openai",
    description="SQL functions for calling OpenAI APIs",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Simon Willison",
    url="https://github.com/simonw/datasette-openai",
    project_urls={
        "Issues": "https://github.com/simonw/datasette-openai/issues",
        "CI": "https://github.com/simonw/datasette-openai/actions",
        "Changelog": "https://github.com/simonw/datasette-openai/releases",
    },
    license="Apache License, Version 2.0",
    classifiers=[
        "Framework :: Datasette",
        "License :: OSI Approved :: Apache Software License",
    ],
    version=VERSION,
    packages=["datasette_openai"],
    entry_points={"datasette": ["openai = datasette_openai"]},
    install_requires=["datasette", "regex"],
    extras_require={"test": ["pytest", "pytest-asyncio"]},
    python_requires=">=3.7",
)
