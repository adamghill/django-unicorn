import nox


@nox.session()
@nox.parametrize("django", ["2.2", "3.0", "3.2"])
def tests(session, django):
    session.install("poetry")
    session.run("poetry", "install", "-E", "minify")
    session.install(f"django=={django}")
    session.run("pytest", "-m", "not slow")
    session.run("pytest", "-m", "slow")
