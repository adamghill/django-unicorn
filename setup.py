#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This is a temporary solution for the fact that `pip install -e`
# fails when there is not a `setup.py`.

import re
from distutils.core import setup
from pathlib import Path


def get_version():
    """
    Grabs the version from pyproject.toml. Uses regex to avoid installing a dependency.
    """

    pyproject_path = Path("pyproject.toml")
    version = "0.1.0"

    if pyproject_path.exists():
        with open(pyproject_path) as f:
            pyproject_toml = f.read()
            s = re.search(r"version\s*=\s*\"(.*?)\"", pyproject_toml)

            if s.groups():
                version = s.groups()[0]

    return version


# TODO: read package name with regex
setup(name="django-unicorn", version=get_version())
