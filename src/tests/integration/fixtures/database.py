import shutil
import pandas as pd
import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine import URL


@pytest.fixture(autouse=True)
def run_around_tests(tmpdir_factory):
    my_tmpdir = tmpdir_factory.mktemp("tmp")
    yield my_tmpdir
    shutil.rmtree(str(my_tmpdir))


databaseConfig = {
    "postgreSQL": {
        "drivername": "postgresql",
        "username": "ploomber_app",
        "password": "ploomber_app_password",
        "database": "db",
        "host": "localhost",
        "port": "5432",
        "alias": "postgreSQLTest",
    },
    "mySQL": {
        "drivername": "mysql+pymysql",
        "username": "ploomber_app",
        "password": "ploomber_app_password",
        "database": "db",
        "host": "localhost",
        "port": "33306",
        "alias": "mySQLTest",
    },
    "SQLite": {
        "drivername": "sqlite",
        "username": None,
        "password": None,
        "database": "/tmp/db-sqlite",
        "host": None,
        "port": None,
        "alias": "SQLiteTest",
    },
    "duckDB": {
        "drivername": "duckdb",
        "username": None,
        "password": None,
        "database": "/tmp/db-duckdb",
        "host": None,
        "port": None,
        "alias": "duckDBTest",
    },
}


# SQLAlchmey URL: https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls
def get_database_url(database, static_db=False):
    return URL.create(
        drivername=databaseConfig[database]["drivername"],
        username=databaseConfig[database]["username"],
        password=databaseConfig[database]["password"],
        host=databaseConfig[database]["host"],
        port=databaseConfig[database]["port"],
        database=databaseConfig[database]["database"],
    ).render_as_string(hide_password=False)


def load_taxi_data(engine):
    table_name = "taxi"
    df = pd.DataFrame(
        {"taxi_driver_name": ["Eric Ken", "John Smith", "Kevin Kelly"] * 15}
    )
    df.to_sql(name=table_name, con=engine, chunksize=100_000, if_exists="replace")


@pytest.fixture(scope="session")
def setup_postgreSQL():
    engine = create_engine(get_database_url("postgreSQL"))
    # Load taxi_data
    load_taxi_data(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def ip_with_postgreSQL(ip, setup_postgreSQL):
    configKey = "postgreSQL"
    alias = databaseConfig[configKey]["alias"]

    # Disconnect build-in sqlite connection
    ip.run_cell("%sql --close sqlite://")
    # Select database engine
    ip.run_cell("%sql " + get_database_url("postgreSQL") + " --alias " + alias)
    yield ip
    # Disconnect database
    ip.run_cell("%sql -x " + alias)


@pytest.fixture(scope="session")
def setup_mySQL():
    engine = create_engine(get_database_url("mySQL"))
    # Load taxi_data
    load_taxi_data(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def ip_with_mySQL(ip, setup_mySQL):
    configKey = "mySQL"
    alias = databaseConfig[configKey]["alias"]

    # Disconnect build-in sqlite connection
    ip.run_cell("%sql --close sqlite://")
    # Select database engine
    ip.run_cell("%sql " + get_database_url("mySQL") + " --alias " + alias)
    yield ip
    # Disconnect database
    ip.run_cell("%sql -x " + alias)


@pytest.fixture(scope="session")
def setup_SQLite():
    engine = create_engine(get_database_url("SQLite"))
    # Load taxi_data
    load_taxi_data(engine)

    yield engine
    engine.dispose()


@pytest.fixture
def ip_with_SQLite(ip, setup_SQLite):
    configKey = "SQLite"
    alias = databaseConfig[configKey]["alias"]

    # Disconnect build-in sqlite connection
    ip.run_cell("%sql --close sqlite://")
    # Select database engine, use different sqlite database endpoint
    ip.run_cell("%sql " + get_database_url(configKey) + " --alias " + alias)
    yield ip
    # Disconnect database
    ip.run_cell("%sql -x " + alias)


@pytest.fixture(scope="session")
def setup_duckDB():
    engine = create_engine(get_database_url("duckDB"))
    # Load taxi_data
    load_taxi_data(engine)

    yield engine
    engine.dispose()


@pytest.fixture
def ip_with_duckDB(ip, setup_duckDB):
    configKey = "duckDB"
    alias = databaseConfig[configKey]["alias"]

    # Disconnect build-in sqlite connection
    ip.run_cell("%sql --close sqlite://")
    # Select database engine, use different sqlite database endpoint
    ip.run_cell("%sql " + get_database_url(configKey) + " --alias " + alias)
    yield ip
    # Disconnect database
    ip.run_cell("%sql -x " + alias)
