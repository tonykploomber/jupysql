import sys
from unittest.mock import Mock, patch
import pytest
from sqlalchemy.engine import Engine
import sql.connection
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


def test_password_isnt_displayed(mock_postgres):
    Connection.from_connect_str("postgresql://user:topsecret@somedomain.com/db")

    assert "topsecret" not in Connection.connection_list()


def test_connection_name(mock_postgres):
    conn = Connection.from_connect_str("postgresql://user:topsecret@somedomain.com/db")

    assert conn.name == "user@db"


def test_alias(cleanup):
    Connection.from_connect_str("sqlite://", alias="some-alias")

    assert list(Connection.connections) == ["some-alias"]


def test_get_curr_connection_info(mock_postgres):
    Connection.from_connect_str("postgresql://user:topsecret@somedomain.com/db")
    assert Connection._get_curr_connection_info() == {
        "dialect": "postgresql",
        "driver": "psycopg2",
        "server_version_info": None,
    }


def test_get_curr_sqlglot_dialect_no_curr_connection(monkeypatch):
    monkeypatch.setattr(Connection, "_get_curr_connection_info", lambda: None)
    assert Connection._get_curr_sqlglot_dialect() is None


@pytest.mark.parametrize(
    "sqlalchemy_connection_info, expected_sqlglot_dialect",
    [
        (
            {
                "dialect": "duckdb",
                "driver": "duckdb_engine",
                "server_version_info": [8, 0],
            },
            "duckdb",
        ),
        (
            {
                "dialect": "mysql",
                "driver": "pymysql",
                "server_version_info": [10, 10, 3, 10, 3],
            },
            "mysql",
        ),
        # sqlalchemy and sqlglot have different dialect name, test the mapping dict
        (
            {
                "dialect": "sqlalchemy_mock_dialect_name",
                "driver": "sqlalchemy_mock_driver_name",
                "server_version_info": [0],
            },
            "sqlglot_mock_dialect",
        ),
        (
            {
                "dialect": "only_support_in_sqlalchemy_dialect",
                "driver": "sqlalchemy_mock_driver_name",
                "server_version_info": [0],
            },
            "only_support_in_sqlalchemy_dialect",
        ),
    ],
)
def test_get_curr_sqlglot_dialect(
    monkeypatch, sqlalchemy_connection_info, expected_sqlglot_dialect
):
    monkeypatch.setattr(
        Connection, "_get_curr_connection_info", lambda: sqlalchemy_connection_info
    )
    monkeypatch.setattr(
        sql.connection,
        "DIALECT_NAME_SQLALCHEMY_TO_SQLGLOT_MAPPING",
        {"sqlalchemy_mock_dialect_name": "sqlglot_mock_dialect"},
    )
    assert Connection._get_curr_sqlglot_dialect() == expected_sqlglot_dialect


@pytest.mark.parametrize(
    "cur_dialect, expected_support_backtick",
    [
        ("mysql", True),
        ("sqlite", True),
        ("postgres", False),
    ],
)
def test_is_curr_dialect_support_backtick(
    monkeypatch, cur_dialect, expected_support_backtick
):
    monkeypatch.setattr(Connection, "_get_curr_sqlglot_dialect", lambda: cur_dialect)
    assert Connection._is_curr_dialect_support_backtick() == expected_support_backtick


def test_is_curr_dialect_support_backtick_sqlglot_missing_dialect(monkeypatch):
    monkeypatch.setattr(
        Connection, "_get_curr_sqlglot_dialect", lambda: "something_weird_dialect"
    )
    with pytest.raises(ValueError):
        Connection._is_curr_dialect_support_backtick()


# Mock the missing package
# Ref: https://stackoverflow.com/a/28361013
def test_missing_duckdb_dependencies(cleanup, monkeypatch):
    with patch.dict(sys.modules):
        sys.modules["duckdb"] = None
        sys.modules["duckdb-engine"] = None

        with pytest.raises(UsageError) as error:
            Connection.from_connect_str("duckdb://")
        assert "try to install package: duckdb-engine" + str(error.value)


@pytest.mark.parametrize(
    "missing_pkg, except_missing_pkg_suggestion, connect_str",
    [
        # MySQL + MariaDB
        ["pymysql", "pymysql", "mysql+pymysql://"],
        ["mysqlclient", "mysqlclient", "mysql+mysqldb://"],
        ["mariadb", "mariadb", "mariadb+mariadbconnector://"],
        ["mysql-connector-python", "mysql-connector-python", "mysql+mysqlconnector://"],
        ["asyncmy", "asyncmy", "mysql+asyncmy://"],
        ["aiomysql", "aiomysql", "mysql+aiomysql://"],
        ["cymysql", "cymysql", "mysql+cymysql://"],
        ["pyodbc", "pyodbc", "mysql+pyodbc://"],
        # PostgreSQL
        ["psycopg2", "psycopg2", "postgresql+psycopg2://"],
        ["psycopg", "psycopg", "postgresql+psycopg://"],
        ["pg8000", "pg8000", "postgresql+pg8000://"],
        ["asyncpg", "asyncpg", "postgresql+asyncpg://"],
        ["psycopg2cffi", "psycopg2cffi", "postgresql+psycopg2cffi://"],
        # Oracle
        ["cx_oracle", "cx_oracle", "oracle+cx_oracle://"],
        ["oracledb", "oracledb", "oracle+oracledb://"],
        # MSSQL
        ["pyodbc", "pyodbc", "mssql+pyodbc://"],
        ["pymssql", "pymssql", "mssql+pymssql://"],
    ],
)
def test_missing_driver(
    missing_pkg, except_missing_pkg_suggestion, connect_str, monkeypatch
):
    with patch.dict(sys.modules):
        sys.modules[missing_pkg] = None
        with pytest.raises(UsageError) as error:
            Connection.from_connect_str(connect_str)

        assert "try to install package: " + missing_pkg in str(error.value)


def test_no_current_connection_and_get_info(monkeypatch):
    monkeypatch.setattr(Connection, "current", None)
    assert Connection._get_curr_connection_info() is None
