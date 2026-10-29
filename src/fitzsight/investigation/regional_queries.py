"""Approved regional aggregate queries; windows use bound parameters."""


def regional_sql(table: str) -> str:
    deposit_sql = (
        "SELECT c.region, COUNT(DISTINCT c.customer_id) AS customer_count, "
        "COALESCE(SUM(CAST(d.amount AS DOUBLE)), 0) AS deposits, "
        "SUM(CASE WHEN d.customer_id IS NOT NULL AND (d.currency IS NULL OR d.currency <> 'USD') THEN 1 ELSE 0 END) AS invalid_currency_count "
        "FROM customers c LEFT JOIN deposits d ON d.customer_id = c.customer_id "
        "AND d.status = 'completed' AND d.timestamp >= ? AND d.timestamp < ? "
        "GROUP BY c.region ORDER BY c.region"
    )
    withdrawal_sql = (
        "SELECT c.region, COALESCE(SUM(CAST(w.amount AS DOUBLE)), 0) AS withdrawals, "
        "SUM(CASE WHEN w.customer_id IS NOT NULL AND (w.currency IS NULL OR w.currency <> 'USD') THEN 1 ELSE 0 END) AS invalid_currency_count "
        "FROM customers c LEFT JOIN withdrawals w ON w.customer_id = c.customer_id "
        "AND w.status = 'completed' AND w.timestamp >= ? AND w.timestamp < ? "
        "GROUP BY c.region ORDER BY c.region"
    )
    if table == "deposits":
        return deposit_sql
    if table == "withdrawals":
        return withdrawal_sql
    raise ValueError("Unsupported regional cash-flow table")
