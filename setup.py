"""Packaging amlib and amcli"""
from setuptools import setup, find_namespace_packages, find_packages

setup(
    name="pylerttool",
    version="0.1.7",
    author="Oliver Nispel",
    author_email="oliver@nispel.org",
    install_requires=[
        "requests",
        "pydantic==1.*",
        "click",
        "tabulate",
        "pyyaml",
        "pytimeparse",
    ],
    include_package_data=True,
    packages=find_namespace_packages(where="src"),
    package_dir={
        "": "src",
    },
    entry_points = {
        'console_scripts': [
            'amcli = amlib.am_cli:main_cli'
        ]
    },
    python_requires=">=3.10",
)
