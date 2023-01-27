from pathlib import Path
from unittest.mock import Mock
import pytest
import urllib.request
import duckdb
from sql.telemetry import telemetry
from sql import plot

@pytest.fixture
def simple_db_conn():
    if not Path("iris.csv").is_file():
        urllib.request.urlretrieve(
            "https://raw.githubusercontent.com/plotly/datasets/master/iris-data.csv",
            "iris.csv",
        )
    conn = duckdb.connect(database=":memory:")
    return conn

@pytest.fixture
def mock_log_api(monkeypatch):
    mock_log_api = Mock()
    monkeypatch.setattr(telemetry, 'log_api', mock_log_api)
    yield mock_log_api

def test_boxplot_telemetry(mock_log_api, simple_db_conn):
    # Test the injected log_api gets called  
    plot.boxplot("iris.csv", "petal width", conn=simple_db_conn)

    mock_log_api.assert_called()

def test_histogram_telemetry(mock_log_api, simple_db_conn):
    # Test the injected log_api gets called  
    plot.histogram("iris.csv", "petal width", bins=50, conn=simple_db_conn)

    mock_log_api.assert_called()
