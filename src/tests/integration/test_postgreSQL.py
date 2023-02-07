# flake8: noqa
from fixtures.database import *


def test_meta_cmd_display(ip_with_postgreSQL):
    out = ip_with_postgreSQL.run_cell("%sql \d")
    assert len(out.result) > 0
    assert ("public", "taxi", "table", "ploomber_app") in out.result
