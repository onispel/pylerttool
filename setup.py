"""Packaging amlib and amcli"""
from setuptools import setup, find_namespace_packages, find_packages

setup(
    name="pylerttool",
    version="0.1.0-dev",
    author="Oliver Nispel",
    install_requires=[
        "requests",
        "pydantic",
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
            'amcli = amcli.am_cli:main_cli'
        ]
    },
    python_requires=">=3.10",
)
