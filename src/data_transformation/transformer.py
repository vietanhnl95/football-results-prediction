def transform(conn, query, des_table):
    # check table exist
    

    # execute create table query
    try:
        conn.execute(f"""CREATE TABLE {des_table} AS {query}""")
        print('Transform Successfully')
    except Exception as e:
        print('Transform Failed')
        print('Error: \n', e)
