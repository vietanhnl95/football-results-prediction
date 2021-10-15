import json
import pandas as pd
import datetime
import sqlalchemy
import utils


def main():
    """
    Request to API and insert data to DB
    """
    #read_config
    config = utils.read_config()
    leagues_config = config['leagues']

    # connect to db
    db_url = config['db_url']
    conn = utils.create_db_connection(db_url)

    # get api response
    response = utils.get_api_response("https://api-football-v1.p.rapidapi.com/v3/leagues")

    # convert to dataframe
    df = pd.json_normalize(response['response'], sep = '_')

    # import to db
    df['created_at'] = datetime.datetime.now()
    df.to_sql(
        schema=leagues_config['destination']['schema'],
        name=leagues_config['destination']['table_name'],
        con=conn,
        if_exists='replace',
        dtype={'seasons': sqlalchemy.types.JSON}
    )
    print('DB insert success')
    

if __name__ == '__main__':
    main()
