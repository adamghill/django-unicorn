import nox


@nox.session()
def tests(session):
    session.install("poetry")
    session.run("poetry", "install", "-E", "minify")
    session.run("pytest", "-m", "not slow")
    session.run("pytest", "-m", "slow")
