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

    # connect to db
    db_url = config['main']['db_url']
    conn = utils.create_db_connection(db_url)

    # get current season teams
    def get_teams_by_league_current_season():
        leagues = config['main']['scope']['leagues']
        season_last = config['main']['scope']['season_last']

        for league in leagues:
            response = utils.get_api_response(
                url="https://api-football-v1.p.rapidapi.com/v3/teams",
                querystring={"league": league, "season": season_last}
            )


    # query team_id list
    get_team_id_query = """
	SELECT
		DISTINCT
		teams_home_id AS team_id
	FROM football_api.fixtures

	UNION

	SELECT
		DISTINCT
		teams_away_id AS team_id
	FROM football_api.fixtures
    """
    df_team_ids = pd.read_sql(get_team_id_query, conn)

    # get unique team_id list and sort
    team_ids = sorted(list(df_team_ids['team_id'].unique()))

    # get each team information
    all_response =
    for team_id in team_ids:
        response = utils.get_api_response(
            url="https://api-football-v1.p.rapidapi.com/v3/teams",
            querystring={"id": team_id}
        )

    #


if __name__ == '__main__':
    main()
