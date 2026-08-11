import pytest

from fitzsight.tools.sql import SQLSafetyError, validate_read_only_sql


def test_select_and_cte_are_allowed():
    assert validate_read_only_sql("SELECT 1") == "SELECT 1"
    assert validate_read_only_sql("WITH x AS (SELECT 1 AS a) SELECT a FROM x;").startswith("WITH")


@pytest.mark.parametrize(
    "query",
    [
        "DROP TABLE customers",
        "UPDATE customers SET region='x'",
        "SELECT * FROM customers; DELETE FROM customers",
        "SELECT * FROM read_csv_auto('/tmp/secret.csv')",
        "SELECT 1 -- hidden mutation",
        "PRAGMA show_tables",
    ],
)
def test_unsafe_queries_are_rejected(query):
    with pytest.raises(SQLSafetyError):
        validate_read_only_sql(query)
