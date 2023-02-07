import pandas as pd
import pytest
from sqlalchemy import create_engine


# SQLAlchmey URL: https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls
def get_database_url(database):
    return "{}://{}:{}@{}:{}/{}".format(
        databaseConfig[database]["drivername"],
        databaseConfig[database]["username"],
        databaseConfig[database]["password"],
        databaseConfig[database]["host"],
        databaseConfig[database]["port"],
        databaseConfig[database]["database"],
    )


def get_SQLite_database_url(database="SQLite"):
    return "{}:///{}.db".format(
        databaseConfig[database]["drivername"],
        databaseConfig[database]["database"],
    )


databaseConfig = {
    "postgreSQL": {
        "drivername": "postgresql",
        "username": "ploomber_app",
        "password": "ploomber_app_password",
        "database": "db",
        "host": "localhost",
        "port": "5432",
        "alias": "postgreSQLTest",
        "url_formatter": get_database_url,
    },
    "mySQL": {
        "drivername": "mysql+pymysql",
        "username": "ploomber_app",
        "password": "ploomber_app_password",
        "database": "db",
        "host": "localhost",
        "port": "33306",
        "alias": "mySQLTest",
        "url_formatter": get_database_url,
    },
    "SQLite": {
        "drivername": "sqlite",
        "username": "",
        "password": "",
        "database": "db",
        "host": "",
        "port": "",
        "alias": "SQLiteTest",
        "url_formatter": get_SQLite_database_url,
    },
}


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
    # Disconnect build-in sqlite connection
    ip.run_cell("%sql --close sqlite://")
    # Select database engine
    ip.run_cell(
        "%sql "
        + get_database_url("postgreSQL")
        + " --alias "
        + databaseConfig["postgreSQL"]["alias"]
    )
    yield ip
    # Disconnect database
    ip.run_cell("%sql -x " + databaseConfig["postgreSQL"]["alias"])


@pytest.fixture(scope="session")
def setup_mySQL():
    engine = create_engine(get_database_url("mySQL"))
    # Load taxi_data
    load_taxi_data(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def ip_with_mySQL(ip, setup_mySQL):
    # Disconnect build-in sqlite connection
    ip.run_cell("%sql --close sqlite://")
    # Select database engine
    ip.run_cell(
        "%sql "
        + get_database_url("mySQL")
        + " --alias "
        + databaseConfig["mySQL"]["alias"]
    )
    yield ip
    # Disconnect database
    ip.run_cell("%sql -x " + databaseConfig["mySQL"]["alias"])


@pytest.fixture(scope="session")
def setup_SQLite():
    engine = create_engine(get_SQLite_database_url())
    # Load taxi_data
    load_taxi_data(engine)

    yield engine
    engine.dispose()


@pytest.fixture
def ip_with_SQLite(ip, setup_SQLite):
    # # Disconnect build-in sqlite connection
    ip.run_cell("%sql --close sqlite://")
    # # Select database engine, use different sqlite database endpoint
    ip.run_cell("%sql " + get_SQLite_database_url() + " --alias SQLiteTest")
    yield ip
    # Disconnect database
    ip.run_cell("%sql -x SQLiteTest")
