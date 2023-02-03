import pandas as pd
import pytest
from sqlalchemy import create_engine

postgreSQLConfig = {
    "db_name": "db",
    "user": "ploomber_app",
    "password": "ploomber_app_password",
    "root_password": "ploomber_app_root_password",
}


@pytest.fixture(scope="session")
def setup_mySQL():
    engine = create_engine(
        "mysql+pymysql://ploomber_app:ploomber_app_password@localhost:33306/db"
    )

    yield engine
    engine.dispose()


@pytest.fixture
def taxi_data(setup_mySQL):
    table_name = "taxi"
    engine = setup_mySQL
    df = pd.read_parquet(
        "https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2022-01.parquet"
    )
    df.to_sql(name=table_name, con=engine, chunksize=100_000, if_exists="replace")
    yield table_name
    # delete_table(table_name)


def test_mySQL_query(ip, taxi_data):
    ip.run_cell(
        "%sql mysql+pymysql://ploomber_app:ploomber_app_password@localhost:33306/db"
    )
    out = ip.run_cell("%sql SELECT * FROM taxi LIMIT 3")
    print(out)
