import utils
import pandas as pd

db_url = utils.read_config()['db_url']
conn = utils.create_db_connection(db_url)

sql_command = "SELECT COUNT(*) FROM football_api.fixtures WHERE league_id=39"
result = pd.read_sql(sql_command, con=conn)
print(result.loc[0, 'count'])
