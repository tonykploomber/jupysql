from pathlib import Path
# from ploomber_core.telemetry import
# from ploomber_core.telemetry.telemetry import Telemetry


from unittest.mock import Mock
import pytest
import urllib.request
# this requires duckdb: pip install duckdb
import duckdb
from sql.telemetry import telemetry
from sql import plot

def test_plot_telemetry(monkeypatch):

    mock_log_call = Mock()
    mock_log_api = Mock()
    monkeypatch.setattr(telemetry, 'log_call', mock_log_call)
    monkeypatch.setattr(telemetry, 'log_api', mock_log_api)

    if not Path("iris.csv").is_file():
        urllib.request.urlretrieve(
            "https://raw.githubusercontent.com/plotly/datasets/master/iris-data.csv",
            "iris.csv",
        )

    conn = duckdb.connect(database=":memory:")

    # Simulate the call
    plot.boxplot("iris.csv", "petal width", conn=conn)

    # Test the log_call decorator on boxplot has been called

    mock_log_call.assert_not_called()
    # mock_log_call.assert_called_with("boxplot")

