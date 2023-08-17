def test_query_count(ip_with_clickhouse, test_table_name_dict):
    out = ip_with_clickhouse.run_line_magic(
        "sql",
        f"""
        SELECT *
        FROM {test_table_name_dict['taxi']}
        LIMIT 3;
        """,
    )

    assert len(out) == 3
