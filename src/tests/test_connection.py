import sys
from unittest.mock import Mock
import pytest
from sqlalchemy.engine import Engine
from sql.connection import Connection
from IPython.core.error import UsageError


@pytest.fixture
def cleanup():
    yield
    Connection.connections = {}


@pytest.fixture
def mock_postgres(monkeypatch, cleanup):
    monkeypatch.setitem(sys.modules, "psycopg2", Mock())
    monkeypatch.setattr(Engine, "connect", Mock())


@pytest.fixture
def mock_missing_pymysql_pkg(monkeypatch, cleanup):
    monkeypatch.setitem(sys.modules, "pymysql", None)
    monkeypatch.setattr(Engine, "connect", Mock())


@pytest.fixture
def mock_missing_duckdb_pkg(monkeypatch, cleanup):
    monkeypatch.setitem(sys.modules, "duckdb", None)
    monkeypatch.setattr(Engine, "connect", Mock())


def test_password_isnt_displayed(mock_postgres):
    Connection.from_connect_str("postgresql://user:topsecret@somedomain.com/db")

    assert "topsecret" not in Connection.connection_list()


def test_connection_name(mock_postgres):
    conn = Connection.from_connect_str("postgresql://user:topsecret@somedomain.com/db")

    assert conn.name == "user@db"


def test_alias(cleanup):
    Connection.from_connect_str("sqlite://", alias="some-alias")

    assert list(Connection.connections) == ["some-alias"]


def test_missing_pymysql(mock_missing_pymysql_pkg):
    with pytest.raises(UsageError) as error:
        Connection.from_connect_str(
            "mysql+pymysql://user:topsecret@somedomain.com/db"
        )
    assert "To fix it, try to install the missing module: pymysql" in str(error.value)


def test_missing_duck(mock_missing_duckdb_pkg):
    with pytest.raises(UsageError) as error:
        Connection.from_connect_str("duckdb://")
    assert "To fix it, try to install the missing module: duckdb" in str(error.value)
