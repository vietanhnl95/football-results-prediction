import os
import numpy as np
import pandas as pd
from pandasql import sqldf
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")

from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, f1_score
from yellowbrick.model_selection import learning_curve
from yellowbrick.classifier.confusion_matrix import confusion_matrix
from yellowbrick.classifier.rocauc import roc_auc
from sklearn.naive_bayes import BernoulliNB

import neptune.new as neptune
# init neptune
run = neptune.init(project='vietanh.work/football-match-prediction',
                   api_token='eyJhcGlfYWRkcmVzcyI6Imh0dHBzOi8vYXBwLm5lcHR1bmUuYWkiLCJhcGlfdXJsIjoiaHR0cHM6Ly9hcHAubmVwdHVuZS5haSIsImFwaV9rZXkiOiI1OGQwNDQyOC04MmY5LTRhOTItOGIxOS0xOWY0MzE5NGJmMTMifQ==') # your credentials


# LOAD DATA
matches = pd.read_csv('data/matches.csv')

# FEATURE ENGINEERING
matches['season_start'] = matches['season'].apply(lambda x: x.split('/')[0])
df = matches.query("competition=='Premier League' and season_start > '2013'")

# get recent form of home team
recent_form_home = sqldf("""
select
    df.home_team,
    df.match_date_dt,
    df.home_score,
    avg(case
            when date(df1.match_date_dt) >= date(df.match_date_dt, '-1 month')
                and date(df1.match_date_dt) < date(df.match_date_dt)
                and df.home_team = df1.home_team
            then df1.home_score
            when date(df1.match_date_dt) >= date(df.match_date_dt, '-1 month')
                and date(df1.match_date_dt) < date(df.match_date_dt)
                and df.home_team = df1.away_team
            then df1.away_score
            else 0
        end) as home_score_avg_t30,
    avg(case
            when date(df1.match_date_dt) >= date(df.match_date_dt, '-3 months')
                and date(df1.match_date_dt) < date(df.match_date_dt)
                and df.home_team = df1.home_team
            then df1.home_score
            when date(df1.match_date_dt) >= date(df.match_date_dt, '-3 months')
                and date(df1.match_date_dt) < date(df.match_date_dt)
                and df.home_team = df1.away_team
            then df1.away_score
            else 0
        end) as home_score_avg_t90
from df
left join df df1
    on df.home_team = df1.home_team
    or df.home_team = df1.away_team
group by 1,2,3
order by df.home_team, df.match_date_dt desc
""", globals())

# get recent form of away team
recent_form_away = sqldf("""
select
    df.away_team,
    df.match_date_dt,
    df.away_score,
    avg(case
            when date(df1.match_date_dt) >= date(df.match_date_dt, '-1 month')
                and date(df1.match_date_dt) < date(df.match_date_dt)
                and df.away_team = df1.home_team
            then df1.home_score
            when date(df1.match_date_dt) >= date(df.match_date_dt, '-1 month')
                and date(df1.match_date_dt) < date(df.match_date_dt)
                and df.away_team = df1.away_team
            then df1.away_score
            else 0
        end) as away_score_avg_t30,
    avg(case
            when date(df1.match_date_dt) >= date(df.match_date_dt, '-3 months')
                and date(df1.match_date_dt) < date(df.match_date_dt)
                and df.away_team = df1.home_team
            then df1.home_score
            when date(df1.match_date_dt) >= date(df.match_date_dt, '-3 months')
                and date(df1.match_date_dt) < date(df.match_date_dt)
                and df.away_team = df1.away_team
            then df1.away_score
            else 0
        end) as away_score_avg_t90
from df
left join df df1
    on df.away_team = df1.home_team
    or df.away_team = df1.away_team
group by 1,2,3
order by 1,2 desc
""", globals())

# combine recent forms with the previous data
df2 = sqldf("""
select
    df.*,
    rfh.home_score_avg_t30,
    rfh.home_score_avg_t90,
    rfa.away_score_avg_t30,
    rfa.away_score_avg_t90
from df
left join recent_form_home rfh
    on rfh.home_team = df.home_team and df.match_date_dt = rfh.match_date_dt
left join recent_form_away rfa
    on rfa.away_team = df.away_team and df.match_date_dt = rfa.match_date_dt
""")

# get winner
def get_winner(home_score, away_score):
    if home_score >  away_score:
        return 'home'
    elif home_score == away_score:
        return 'draw'
    else:
        return 'away'

df2['winner'] = df2.apply(lambda df2: get_winner(df2['home_score'], df2['away_score']), axis=1)


# FEATURE SELECTION
df3 = df2[['winner',
           'home_team',
           'away_team',
           'home_score_avg_t30',
           'home_score_avg_t90',
           'away_score_avg_t30',
           'away_score_avg_t90']]
df3.head()


# TRANSFORM
df4 = pd.get_dummies(data=df3, columns=['home_team', 'away_team'])


# TRAIN TEST SPLIT
y = df4['winner']
X = df4.drop(['winner'], axis=1)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=42, stratify=y)


# TRAIN MODEL
def train(model,
          X_train=X_train,
          y_train=y_train,
          X_test=X_test,
          y_test=y_test):

    # fit model
    model.fit(X_train, y_train)
    train_acc = model.score(X_train, y_train)
    train_f1 = f1_score(model.predict(X_train), y_train, average='weighted')

    print('model:', model, '\n -----')

    # training report
    print('train report: \n', classification_report(y_train, model.predict(X_train)), '\n -----')

    # predict
    y_pred = model.predict(X_test)
    test_acc = model.score(X_test, y_test)
    test_f1 = f1_score(y_pred, y_test, average='weighted')

    # test report
    print('test report: \n', classification_report(y_test, y_pred))

    # plot roc_auc
    roc_auc(model, X_train, y_train, X_test, y_test)

    # plot learning curve
    learning_curve(model, X_train, y_train, cv=5, scoring='f1_weighted')


    # plot confusion matrix
    confusion_matrix(model, X_test, y_test, cmap='Blues', fontsize=12)


    # save stats
    model_stats = {
        'model_name': type(model).__name__,
        'train_accuracy': train_acc,
        'train_f1_weighted': train_f1,
        'test_accuracy': test_acc,
        'test_f1_weighted': test_f1
    }

    return model_stats


bnb = BernoulliNB()
bnb_stats = train(bnb)


params = {
    'features': 'match score + recent form 30,90',
    'train_test_split': 'random',
    'model': 'BernoulliNB',
    'hyperpamras': 'default'
}

run['params'] = params
run['model_stats'] = bnb_stats

run.stop()
