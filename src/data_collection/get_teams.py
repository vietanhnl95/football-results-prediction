import json
import pandas as pd
import datetime
import sqlalchemy
import utils


# get current season teams
def get_teams_by_leagues_season(leagues, seasons):
        # declare final result list
    results = []

    # loop and get response
    for league in leagues:
        for season in seasons:
            response = utils.get_api_response(
                url="https://api-football-v1.p.rapidapi.com/v3/teams",
                querystring={"league": league, "season": season_last}
            )
            results.extend(response['response'])

    return results


def main():
    """
    Request to API and insert data to DB
    """
    #read_config
    config = utils.read_config()

    # connect to db
    db_url = config['main']['db_url']
    conn = utils.create_db_connection(db_url)

    # get configs
    leagues = config['main']['scope']['leagues']
    season_first = config['main']['scope']['season_first']
    season_last = config['main']['scope']['season_last']

    teams = get_teams_by_league_season(
        leagues = leagues,
        seasons = range(season_first, season_last, 1)
    )

    df = pd.json_normalize(teams, sep = '_')
    df.drop_duplicates()

    # import to db
    df['created_at'] = datetime.datetime.now()
    df.to_sql(
        schema=config['teams']['destination']['schema'],
        name=config['teams']['destination']['table_name'],
        con=conn,
        if_exists='replace'
    )
    print('DB insert success')


if __name__ == '__main__':
    main()
