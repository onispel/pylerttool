"""Packaging amlib and amcli"""
from setuptools import find_namespace_packages, setup

setup(
    name="pylerttool",
    version="0.0.1",
    author="Oliver Nispel",
    requires=["requests","pydantic","__future__"],
    # install_requires=["requests"],
    include_package_data=True,
    packages=find_namespace_packages(where="src"),
    package_dir={
        "": "src"
    },
    entry_points = {
        'console_scripts': [
            'amcli = amcli.am_cli:main_cli'
        ]
    },
    python_requires=">=3.10",
)
