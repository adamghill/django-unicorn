import sys

import nox


@nox.session()
@nox.parametrize("django", ["2.2", "3.2", "4.0", "4.1"])
def tests(session, django):
    # Skip testing Django 4.0 with Python 3.7 because it is unsupported
    if (
        django.startswith("4.")
        and sys.version_info.major == 3
        and sys.version_info.minor == 7
    ):
        return

    session.install("poetry")
    session.run("poetry", "install", "-E", "minify")
    session.install(f"django=={django}")
    session.run("pytest", "-m", "not slow")
    session.run("pytest", "-m", "slow")
