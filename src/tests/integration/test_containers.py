import os
from sql import _testing

is_on_github = False
if "GITHUB_ACTIONS" in os.environ:
    is_on_github = True


def test_postgres_container():
    if is_on_github:
        return
    with _testing.postgres() as container:
        assert any(
            "database system is ready to accept connections" in str(line, "utf-8")
            for line in container.logs(stream=True)
        )
        assert _testing.database_ready(database="postgreSQL")


def test_mysql_container():
    if is_on_github:
        return
    with _testing.mysql() as container:
        assert any(
            "mysqld: ready for connections" in str(line, "utf-8")
            for line in container.logs(stream=True)
        )
        assert _testing.database_ready(database="mySQL")


def test_mariadb_container():
    if is_on_github:
        return
    with _testing.mariadb() as container:
        assert any(
            "mysqld: ready for connections" in str(line, "utf-8")
            for line in container.logs(stream=True)
        )
        assert _testing.database_ready(database="mariaDB")
