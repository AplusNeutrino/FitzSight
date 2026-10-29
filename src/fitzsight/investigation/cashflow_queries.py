"""Approved cash-flow SQL shared by execution and request-context verification."""


def cashflow_sql(table: str, *, region_filter: bool = True) -> str:
    if table not in {'deposits', 'withdrawals'}:
        raise ValueError('Unsupported cash-flow table')
    region_clause = ' AND c.region = ?' if region_filter else ''
    return (
        'SELECT t.customer_id, t.timestamp, t.amount, t.currency, c.region, c.assigned_team '
        f'FROM {table} AS t JOIN customers AS c ON c.customer_id = t.customer_id '
        "WHERE t.status = 'completed' "
        'AND t.timestamp >= ? AND t.timestamp < ?'
        f'{region_clause} ORDER BY t.timestamp, t.customer_id'
    )
