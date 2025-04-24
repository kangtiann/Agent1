import clickhouse_connect

client = clickhouse_connect.get_client(host='localhost', username='agent')
result = client.query_df('select * from inv.F13 limit 10')
print(str(result))

