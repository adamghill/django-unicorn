import nox


@nox.session()
@nox.parametrize("django", ["3.2", "4.1", "4.2"])
def tests(session, django):
    session.install("poetry")
    session.run("poetry", "install", "-E", "minify")
    session.install(f"django=={django}")
    session.run("pytest", "-m", "not slow")
    session.run("pytest", "-m", "slow")
