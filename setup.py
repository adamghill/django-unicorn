#!/usr/bin/env python

# This is a temporary solution for the fact that `pip install -e`
# fails when there is not a `setup.py`.

import json
from configparser import ConfigParser
from distutils.core import setup


def project_info():
    config = ConfigParser()
    config.read("pyproject.toml")
    project = config["tool.poetry"]
    return {
        "name": json.loads(project["name"]),
        "version": json.loads(project["version"]),
    }


setup(**project_info())
