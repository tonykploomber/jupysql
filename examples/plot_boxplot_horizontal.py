from pathlib import Path
import urllib.request

# this requires duckdb: pip install duckdb
from sql.connection import Connection

from sql import plot


if not Path("iris.csv").is_file():
    urllib.request.urlretrieve(
        "https://raw.githubusercontent.com/plotly/datasets/master/iris-data.csv",
        "iris.csv",
    )

conn = Connection.from_connect_str("duckdb://").session

plot.boxplot("iris.csv", "petal width", conn=conn, orient="h")
