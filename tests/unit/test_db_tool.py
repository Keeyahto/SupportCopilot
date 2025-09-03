import pytest
from apps.api.db_tool import safe_sql


def test_safe_sql_allows_select_and_adds_limit():
    sql = "SELECT * FROM orders"
    out = safe_sql(sql)
    assert out.lower().startswith("select")
    assert "limit" in out.lower()


@pytest.mark.parametrize("bad", [
    "DELETE FROM orders", "DROP TABLE x", "UPDATE t SET a=1", "INSERT INTO t VALUES(1)",
])
def test_safe_sql_blocks_dml(bad):
    with pytest.raises(ValueError):
        safe_sql(bad)

