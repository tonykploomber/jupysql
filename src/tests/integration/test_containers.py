from contextlib import contextmanager
from multiprocessing import Process
import os
import signal
import threading
import time
from sql import _testing
from signal import pthread_kill, SIGTSTP, SIGINT
is_on_github = False
if "GITHUB_ACTIONS" in os.environ:
    is_on_github = True

def test_postgres_container():
    with _testing.postgres(is_bypass_init=is_on_github) as container:
        assert any(
            "database system is ready to accept connections" in str(line, "utf-8")
            for line in container.logs(stream=True)
        )
        assert _testing.database_ready(database="postgreSQL")


def test_mysql_container():
    with _testing.mysql(is_bypass_init=is_on_github) as container:
        assert any(
            "mysqld: ready for connections" in str(line, "utf-8")
            for line in container.logs(stream=True)
        )
        assert _testing.database_ready(database="mySQL")


def test_mariadb_container():
    with _testing.mariadb(is_bypass_init=is_on_github) as container:
        assert any(
            "mysqld: ready for connections" in str(line, "utf-8")
            for line in container.logs(stream=True)
        )
        assert _testing.database_ready(database="mariaDB")
