from dockerctx import new_container, pg_ready
from contextlib import contextmanager
import sys
import time
import docker
from docker import errors

client = docker.from_env()


def mysql_ready(
    host,
    port,
    dbuser="postgres",
    dbpass="password",
    dbname="postgres",
    timeout=20,
    poll_freq=0.2,
):
    """Wait until a postgres instance is ready to receive connections.

    .. note::

        This requires psycopg2 to be installed.

    :type host: str
    :type port: int
    :type timeout: float
    :type poll_freq: float
    """
    import sqlalchemy

    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            eng = sqlalchemy.create_engine(
                "mysql+pymysql://ploomber_app:ploomber_app_password@localhost:33306/db"
            ).connect()
            eng.connect()
            eng.close()
            return True
        except Exception:
            pass
        time.sleep(poll_freq)

    return False


def mariadb_ready(
    host,
    port,
    dbuser="postgres",
    dbpass="password",
    dbname="postgres",
    timeout=20,
    poll_freq=0.2,
):
    """Wait until a postgres instance is ready to receive connections.

    .. note::

        This requires psycopg2 to be installed.

    :type host: str
    :type port: int
    :type timeout: float
    :type poll_freq: float
    """
    import sqlalchemy

    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            eng = sqlalchemy.create_engine(
                "mysql+pymysql://ploomber_app:ploomber_app_password@localhost:33309/db"
            ).connect()
            eng.connect()
            eng.close()
            return True
        except Exception:
            pass
        time.sleep(poll_freq)

    return False


@contextmanager
def postgres():
    try:
        client = docker.from_env(version="auto")
        container = client.containers.get("mariadb")
        yield container
    except errors.NotFound:
        print("Creating new container")
        with new_container(
            new_container_name="postgres",
            image_name="postgres",
            ports={5432: 5432},
            environment={
                "POSTGRES_DB": "db",
                "POSTGRES_USER": "ploomber_app",
                "POSTGRES_PASSWORD": "ploomber_app_password",
            },
            ready_test=lambda: pg_ready(
                host="localhost",
                port=5432,
                dbname="db",
                dbuser="ploomber_app",
                dbpass="ploomber_app_password",
            ),
            healthcheck={
                "test": "pg_isready",
                "interval": 10000000000,
                "timeout": 5000000000,
                "retries": 5,
            },
        ) as container:
            yield container


@contextmanager
def mysql():
    try:
        client = docker.from_env(version="auto")
        container = client.containers.get("mariadb")
        yield container
    except errors.NotFound:
        print("Creating new container")
        with new_container(
            new_container_name="mysql",
            image_name="mysql",
            ports={"3306": "33306"},
            # ports={"33306":3306},
            environment={
                "MYSQL_DATABASE": "db",
                "MYSQL_USER": "ploomber_app",
                "MYSQL_PASSWORD": "ploomber_app_password",
                "MYSQL_ROOT_PASSWORD": "ploomber_app_root_password",
            },
            command="mysqld --default-authentication-plugin=mysql_native_password",
            ready_test=lambda: mysql_ready(host="localhost", port=33306),
            healthcheck={
                "test": [
                    "CMD",
                    "mysqladmin",
                    "ping",
                    "-h",
                    "localhost",
                    "--user=root",
                    "--password=ploomber_app_root_password",
                ],
                "timeout": 5000000000,
            }
            # persist=lambda: True
        ) as container:
            yield container


@contextmanager
def mariadb():
    try:
        client = docker.from_env(version="auto")
        curr = client.containers.get("mariadb")
        yield curr
    except errors.NotFound:
        print("Creating new container")
        with new_container(
            new_container_name="mariadb",
            image_name="mariadb",
            ports={"3306": "33309"},
            environment={
                "MYSQL_DATABASE": "db",
                "MYSQL_USER": "ploomber_app",
                "MYSQL_PASSWORD": "ploomber_app_password",
                "MYSQL_ROOT_PASSWORD": "ploomber_app_root_password",
            },
            command="mysqld --default-authentication-plugin=mysql_native_password",
            ready_test=lambda: mariadb_ready(host="localhost", port=33309),
            # ready_test=lambda: time.sleep(50000) or True,
            healthcheck={
                "test": [
                    "CMD",
                    "mysqladmin",
                    "ping",
                    "-h",
                    "localhost",
                    "--user=root",
                    "--password=ploomber_app_root_password",
                ],
                "timeout": 5000000000,
            },
        ) as container:
            yield container


if __name__ == "__main__":
    print("I am running as module")

    with postgres(), mysql(), mariadb():
        try:
            while True:
                time.sleep(5)
        except KeyboardInterrupt:
            print("User press out")
            sys.exit()
