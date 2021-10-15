import json
import pandas as pd
import datetime
import sqlalchemy
import utils


def main():
    """
    Request to API and insert data to DB
    """
    # read_config
    config = utils.read_config()
    fixtures_config = config['fixtures']
    leagues = fixtures_config['leagues']
    season_start = int(fixtures_config['season_start'])
    season_end = int(fixtures_config['season_end'])
    schema = fixtures_config['destination']['schema']
    table = fixtures_config['destination']['table_name']

    # connect to db
    db_url = config['db_url']
    conn = utils.create_db_connection(db_url)

    # Drop table first to perform a full replace
    if fixtures_config['destination']['replace'] == True:
        conn.execute(f"DROP TABLE {schema}.{table}")
        print('Table deleted')

    # request and get data
    for league_id in leagues:
        for season_id in range(season_start, season_end + 1, 1):
            response = utils.get_api_response(url="https://api-football-v1.p.rapidapi.com/v3/fixtures",
                                              querystring={"league":league_id, "season":season_id})

            # convert to dataframe
            df = pd.json_normalize(response['response'], sep = '_')

            # import to db
            df['created_at'] = datetime.datetime.now()
            df.to_sql(
                schema=schema,
                name=table,
                con=conn,
                if_exists='append'
            )
            print('DB insert success')

if __name__ == '__main__':
    main()
