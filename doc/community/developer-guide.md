---
jupytext:
  notebook_metadata_filter: myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.14.5
kernelspec:
  display_name: jupysql
  language: python
  name: jupysql
myst:
  html_meta:
    description lang=en: JupySQL's developer guide
    keywords: jupyter, sql, jupysql
    property=og:locale: en_US
---

# Developer guide

Before continuing, ensure you have a working [development environment.](https://ploomber-contributing.readthedocs.io/en/latest/contributing/setup.html)

+++

## Unit testing

### Running tests

Unit tests are executed on each PR; however, you might need to run them locally.

To run all unit tests:

```sh
pytest --ignore=src/tests/integration
```

To run a specific file:

```sh
pytest src/tests/TEST_FILE_NAME.py
```

### Magics (e.g., `%sql`, `%%sql`, etc)

This guide will show you the basics of writing unit tests for JupySQL magics. Magics are commands that begin with `%` (line magics) and `%%` (cell magics).

In the unit testing suite, there are a few pytest fixtures that prepare the environment so you can get started:

- `ip_empty` - Empty IPython session
- `ip` - IPython session with some sample data

So a typical test will look like this:

```{code-cell} ipython3
def test_something(ip):
    ip.run_cell("%sql sqlite://")
    result = ip.run_cell(
        """%%sql
    SELECT * FROM test
    """
    )

    assert result.success
```

To see some sample tests, [click here.](https://github.com/ploomber/jupysql/blob/master/src/tests/test_magic.py)


The IPython sessions are created like this:

```{code-cell} ipython3
from IPython.core.interactiveshell import InteractiveShell
from sql.magic import SqlMagic

ip_session = InteractiveShell()
ip_session.register_magics(SqlMagic)
```

To run some code:

```{code-cell} ipython3
out = ip_session.run_cell("1 + 1")
```

To test the output:

```{code-cell} ipython3
assert out.result == 2
```

You can also check for execution success:

```{code-cell} ipython3
assert out.success
```

```{important}
Always check for success! Since `run_cell` won't raise an error if the code fails
```

```{code-cell} ipython3
try:
    ip_session.run_cell("1 / 0")
except Exception as e:
    print(f"Error: {e}")
else:
    print("No error")
```

Note that the `run_cell` only printed the error but did not raise an exception.

+++

#### Capturing errors

Let's see how to test that the code raises an expected error:

```{code-cell} ipython3
out = ip_session.run_cell("1 / 0")
```

```{code-cell} ipython3
# this returns the raised exception
out.error_in_exec
```

```{code-cell} ipython3
:tags: [raises-exception]

# this raises the error
out.raise_error()
```

You can then use pytest to check the error:

```{code-cell} ipython3
import pytest
```

```{code-cell} ipython3
with pytest.raises(ZeroDivisionError):
    out.raise_error()
```

To check the error message:

```{code-cell} ipython3
with pytest.raises(ZeroDivisionError) as excinfo:
    out.raise_error()
```

```{code-cell} ipython3
assert str(excinfo.value) == "division by zero"
```

## Integration tests

Integration tests check compatibility with different databases. They are executed on
each PR; however, you might need to run them locally.

```{note}
Setting up the development environment for running integration tests locally
is challenging given the number of dependencies. If you have problems,
[message us on Slack.](https://ploomber.io/community)
```

Ensure you have [Docker Desktop](https://docs.docker.com/desktop/) before continuing.

To install all dependencies:

```sh
# create development environment (you can skip this if you already executed it)
pkgmt setup

# activate environment
conda activate jupysql

# install depdencies
pip install -e '.[integration]'
```

```{tip}
Ensure Docker is running before continuing!
```

To run all integration tests (the tests are pre-configured to start and shut down
the required Docker images):

```sh
pytest src/tests/integration
```

```{important}
If you're using **Windows**, the command above might get stuck. Send us a [message on Slack](https://ploomber.io/community) if it happens.
```

To run some of the tests:

```sh
pytest src/tests/integration/test_generic_db_operations.py::test_profile_query
```

### Integration tests with cloud databases

We run integration tests against cloud databases like Snowflake, which requires using pre-registered accounts to evaluate their behavior. To initiate these tests, please create a branch in our [ploomber/jupyter repository](https://github.com/ploomber/jupysql).

Please note that if you submit a pull request from a forked repository, the integration testing phase will be skipped because the pre-registered accounts won't be accessible.
## General SQL Clause for Multiple Database Dialects

### Context

As our codebase is expanding, we have noticed that we need to write SQL queries for different database dialects such as MySQL, PostgreSQL, SQLite, and more. Writing and maintaining separate queries for each database can be time-consuming and error-prone.

To address this issue, we can use `sqlglot` to create a construct that can be compiled across multiple SQL dialects. This clause will allow us to write a single SQL query that can be translated to different database dialects, then use it for calculating the metadata (e.g. metadata used by boxplot)

In this document, we'll explain how to build generic SQL constructs and provide examples of how it can be used in our codebase. We will also include instructions on how to add support for additional database dialects.

### Example

We can use [SQLGlot](https://sqlglot.com/sqlglot.html) to build the general sql expressions

Then transpile to the sql which is supported by current connected dialect.

Our `sql.connection.Connection._transpile_query` will automatically detect the dialect and transpile the SQL clause

```python
query = sql.connection.Connection._transpile_query(general_sql)
data = conn.execute(sqlalchemy.sql.text(query)).fetchall()
```

```{code-cell} ipython3
%pip install sqlglot
from sqlglot import select, condition

where = condition("x=1").and_("y=1")
general_sql = select("*").from_("y").where(where).sql()

general_sql
```

Then transpile to the sql which is supported by current connected dialect.

Our `sql.connection.Connection._transpile_query` will automatically detect the dialect and transpile the SQL clause.

+++

### When current connection is via duckdb

```{code-cell} ipython3
from sql import connection
from sqlalchemy import create_engine
conn = connection.Connection(engine=create_engine(url="duckdb://"))
```

### When current connection is via duckdb

```{code-cell} ipython3
from sql import connection
from sqlalchemy import create_engine
from sqlglot import select, condition

# Prepare connection
conn = connection.Connection(engine=create_engine(url="duckdb://"))

# Prepare general SQL clause
where = condition("x=1").and_("y=1")
general_sql = select("*").from_("y").where(where).sql()

conn.transpile_sql(general_sql)
```

```{code-cell} ipython3

```
