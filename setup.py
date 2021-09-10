from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="mkdocs-git-authors-plugin",
    version="0.5",
    description="Mkdocs plugin to display git authors of a page",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="mkdocs git contributors committers authors plugin",
    url="https://github.com/timvink/mkdocs-git-authors-plugin",
    author="Tim Vink",
    author_email="vinktim@gmail.com",
    license="MIT",
    python_requires=">=3.5",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["mkdocs>=1.0"],
    packages=find_packages(),
    entry_points={
        "mkdocs.plugins": [
            "git-authors = mkdocs_git_authors_plugin.plugin:GitAuthorsPlugin"
        ]
    },
)
