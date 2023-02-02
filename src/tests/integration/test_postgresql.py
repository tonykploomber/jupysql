import pandas as pd
import pytest
from sqlalchemy import create_engine

postgreSQLConfig = {
    "db_name": "db",
    "user": "ploomber_app",
    "password": "ploomber_app_password",
}


@pytest.fixture(scope="session")
def setup_postgreSQL():
    engine = create_engine(
        "postgresql://ploomber_app:ploomber_app_password@localhost/db"
    )

    yield engine
    engine.dispose()


@pytest.fixture
def taxi_data(setup_postgreSQL):
    table_name = "taxi"
    engine = setup_postgreSQL
    df = pd.read_parquet(
        "https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2022-01.parquet"
    )
    df.to_sql(name=table_name, con=engine, chunksize=100_000, if_exists="replace")
    yield table_name
    # delete_table(table_name)


# @pytest.fixture
# def delete_table(setup_postgreSQL, table_name):
#     conn = setup_postgreSQL.connect()
#     conn.execute("DROP TABLE " + table_name)
#     conn.close()


@pytest.mark.integration
def test_postgreSQL_query(ip, taxi_data):
    ip.run_cell("%sql postgresql://ploomber_app:ploomber_app_password@localhost/db")
    out = ip.run_cell("%sql SELECT * FROM " + taxi_data + " LIMIT 3")
    print(out)
