from pathlib import Path
from unittest.mock import ANY, Mock
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
    monkeypatch.setattr(telemetry, "log_api", mock_log_api)
    yield mock_log_api


def test_boxplot_telemetry_execution(mock_log_api, simple_db_conn):
    # Test the injected log_api gets called
    plot.boxplot("iris.csv", "petal width", conn=simple_db_conn)

    mock_log_api.assert_called_with(
        action="jupysql-boxplot-success", total_runtime=ANY, metadata=ANY
    )


def test_histogram_telemetry_execution(mock_log_api, simple_db_conn):
    # Test the injected log_api gets called
    plot.histogram("iris.csv", "petal width", bins=50, conn=simple_db_conn)

    mock_log_api.assert_called_with(
        action="jupysql-histogram-success", total_runtime=ANY, metadata=ANY
    )


def test_data_frame_telemetry_execution(mock_log_api, ip):
    # Simulate the cell query & get the DataFrame
    ip.run_cell("%sql duckdb://")
    ip.run_cell("result = %sql SELECT * FROM iris.csv")
    ip.run_cell("result.DataFrame()")

    mock_log_api.assert_called_with(
        action="jupysql-data-frame-success", total_runtime=ANY, metadata=ANY
    )


def test_sqlrender_telemetry_execution(mock_log_api, ip):
    # Simulate the sqlrender query
    ip.run_cell("%sql duckdb://")
    ip.run_cell(
        "%sql --save class_setosa --no-execute \
            SELECT * FROM iris.csv WHERE class='Iris-setosa'"
    )
    ip.run_cell("%sqlrender class_setosa")

    mock_log_api.assert_called_with(
        action="jupysql-sqlrender-success", total_runtime=ANY, metadata=ANY
    )


def test_execute_telemetry_execution(mock_log_api, ip):
    ip.run_cell("%sql duckdb://")

    mock_log_api.assert_called_with(
        action="jupysql-execute-success", total_runtime=ANY, metadata=ANY
    )
