from contextlib import contextmanager
import time
from sql import _testing

# from multiprocessing import Process


def test_start_containers_from_cmd(monkeypatch):
    @contextmanager
    def mockPostgre():
        time.sleep(1)
        yield None

    monkeypatch.setattr("sql._testing.postgres", mockPostgre)
    monkeypatch.setattr("sql._testing.mysql", mockPostgre)
    monkeypatch.setattr("sql._testing.mariadb", mockPostgre)

    # p = Process(target=_testing.main())
    # p.start()
    # time.sleep(3)
    # p.terminate()
    # p.join()

    # _testing.main()


def test_postgres_container():
    with _testing.postgres() as container:
        assert any(
            "database system is ready to accept connections" in str(line, "utf-8")
            for line in container.logs(stream=True)
        )
        assert _testing.database_ready(database="postgreSQL")


def test_mysql_container():
    with _testing.mysql() as container:
        assert any(
            "mysqld: ready for connections" in str(line, "utf-8")
            for line in container.logs(stream=True)
        )
        assert _testing.database_ready(database="mySQL")


def test_mariadb_container():
    with _testing.mariadb() as container:
        assert any(
            "mysqld: ready for connections" in str(line, "utf-8")
            for line in container.logs(stream=True)
        )
        assert _testing.database_ready(database="mariaDB")
