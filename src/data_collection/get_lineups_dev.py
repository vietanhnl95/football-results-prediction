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
    lineups_config = config['lineups']

    # connect to db
    db_url = config['db_url']
    conn = utils.create_db_connection(db_url)

    def get_lineup(fixture_id):
        # get api response
        response = utils.get_api_response(
            url="https://api-football-v1.p.rapidapi.com/v3/fixtures/lineups",
            querystring={"fixture": fixture_id}
        )

        return response

    print(get_lineup('192297'))


if __name__ == "__main__":
    main()
