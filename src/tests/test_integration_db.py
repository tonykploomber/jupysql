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
    df = pd.read_parquet(
        "https://d37ci6vzurychx.cloudfront.net/\
        trip-data/yellow_tripdata_2021-01.parquet"
    )
    engine = create_engine(
        "postgresql://ploomber_app:ploomber_app_password@localhost/db"
    )
    df.to_sql(name="taxi", con=engine, chunksize=100_000)

    yield engine
    engine.dispose()


@pytest.mark.integtest
def test_postgreSQL_query(ip):
    ip.run_cell("%sql postgresql://ploomber_app:ploomber_app_password@localhost/db")
    out = ip.run_cell("%sqlcmd tables")
    print(out)
