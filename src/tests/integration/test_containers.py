import os
import pytest
from sql import _testing

is_on_github = False
if "GITHUB_ACTIONS" in os.environ:
    is_on_github = True


@pytest.mark.parametrize(
    "container_context, excepted_database_ready_string, configKey",
    [
        (
            _testing.postgres,
            "database system is ready to accept connections",
            "postgreSQL",
        ),
        (_testing.mysql, "mysqld: ready for connections", "mySQL"),
        (_testing.mariadb, "mysqld: ready for connections", "mariaDB"),
    ],
)
def test_invidual_container(
    container_context, excepted_database_ready_string, configKey
):
    if is_on_github:
        return
    with container_context() as container:
        assert any(
            excepted_database_ready_string in str(line, "utf-8")
            for line in container.logs(stream=True)
        )
        assert _testing.database_ready(database=configKey)
