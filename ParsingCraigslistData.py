# -*- coding: utf-8 -*-
"""
Created on Wed Feb 27 20:13:30 2019

@author: Konrad
"""
from sqlalchemy import create_engine, text
import yaml
import os
import sys
import psycopg2
import pandas as pd
import time

import datetime
from pytz import timezone

if sys.platform != "linux":
    os.chdir("C:/Users/Konrad/Documents/CraigslistHousing")

    with open("db_info.yml", 'r') as stream:
        try:
            credentials = (yaml.load(stream))
        except yaml.YAMLError as exc:
            print(exc)
    import helpers
else:
    os.chdir("/home/ubuntu/apts")

    with open('db_info.yml', 'r') as stream:
        try:
            credentials = (yaml.load(stream))
        except yaml.YAMLError as exc:
            print(exc)
    import helpers

    os.environ['TZ'] = "US/Pacific"
    time.tzset()

current_date = timezone('US/Pacific').localize(datetime.datetime.now()) 

slack_token = credentials['default']['slack_info']['token']
db_info = credentials['default']['database_info']

apt_list = helpers.get_apt_list()
my_df = helpers.run_parsing(apt_list)

engine = create_engine('postgresql://' + db_info['user'] + ":" + db_info['pwd'] + '@' + 
                   db_info['host'] + ':' + str(5432) + '/' + db_info['dbname'])

helpers.post_new_apts(my_df, engine, current_date)

#helpers.post_to_slack(my_df)