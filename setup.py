from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="mkdocs-git-authors-plugin",
    version="0.9.0",
    description="Mkdocs plugin to display git authors of a page",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="mkdocs git contributors committers authors plugin",
    url="https://github.com/timvink/mkdocs-git-authors-plugin",
    author="Tim Vink",
    author_email="vinktim@gmail.com",
    license="MIT",
    python_requires=">=3.7",
    classifiers=[
        "Operating System :: OS Independent",
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3 :: Only',
        "License :: OSI Approved :: MIT License",
        'Topic :: Documentation',
        'Topic :: Text Processing',
    ],
    install_requires=["mkdocs>=1.0"],
    packages=find_packages(),
    entry_points={
        "mkdocs.plugins": [
            "git-authors = mkdocs_git_authors_plugin.plugin:GitAuthorsPlugin"
        ]
    },
)
