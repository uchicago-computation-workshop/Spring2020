#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#!/usr/bin/env python
# coding: utf-8

# In[184]:


import requests
import pandas as pd
import dateutil
import datetime
import pytz
from collections import Counter
import itertools
import sys
import warnings
warnings.filterwarnings("ignore")


dates = [(4,9),
         (4,30),
         (5,7),
         (5,14),
         (5,21),
         (5,28)]

d = datetime.datetime(2020,4,9)
timezone = pytz.timezone("America/Chicago")
d_aware = timezone.localize(d)
issues = "uchicago-computation-workshop/Spring2020/issues/"
current_github_accept = "application/vnd.github.squirrel-girl-preview+json"
headers = {'Accept': 'application/vnd.github.v3+json'}


def get_react(ID, react_deadline, auth):
    url_r = "https://api.github.com/repos/" + issues + "comments/"
    url = url_r + str(ID) + "/reactions?per_page=100"
    single = requests.get(url, headers = {'Accept': current_github_accept}, auth = auth)
    r_users = single.json()
    if len(r_users) > 0:
        r_df = pd.DataFrame(r_users)
        r_df['created_at_datetime'] = r_df['created_at'].apply(lambda x: dateutil.parser.parse(x))
        valid_r_df = r_df[r_df['created_at_datetime'] < react_deadline]
        valid_users = [user['login'] for user in valid_r_df.user]
    else:
        valid_users = []
    return(valid_users)


def get_weekly_count(week, auth):
    url_c = "https://api.github.com/repos/" + issues + str(week) + "/comments?per_page=100"
    r = requests.get(url_c, headers = headers, auth=auth)
    if r.status_code== 404:
        github_df = None
        empty = True
    else:
        comments = r.json()
        comments_df = pd.DataFrame(comments)
        comments_df['created_at_datetime'] = comments_df['created_at'].apply(lambda x: dateutil.parser.parse(x))
        m, d = dates[week-1]
        comment_deadline = datetime.datetime(2020,m,d,0, tzinfo = d_aware.tzinfo)
        comment_deadline_1 = datetime.datetime(2020,m,d,11, tzinfo = d_aware.tzinfo)
        react_deadline = datetime.datetime(2020,m,d,11, tzinfo = d_aware.tzinfo)
        validcomments_df = comments_df[comments_df['created_at_datetime'] < comment_deadline_1]
        validcomments_df['reactions'] = validcomments_df['id'].apply(lambda x: get_react(x, react_deadline = react_deadline, auth = auth))
        validcomments_users = [user['login'] for user in validcomments_df['user']]
        comments_count = Counter(validcomments_users)
        valid_reactions = validcomments_df['reactions'].tolist()
        merged = list(itertools.chain(*valid_reactions))
        reactions_count = Counter(merged)
        columns = ['comments_%1d_%1d' %(m,d), 'reacts_%1d_%1d' %(m,d)]
        github_df = pd.DataFrame([], columns = columns, index = validcomments_users)
        github_df.iloc[:,0] = pd.Series(comments_count)
        github_df.iloc[:,1] = pd.Series(reactions_count)
        empty = False
    return(github_df, empty)


# In[ ]:


if __name__=="__main__":  
    args = sys.argv
    if len(args)== 3:
        username, password = args[1:]
        auth = (username, password)
        github_df = get_weekly_count(1, auth = auth)[0]
        for i in range(2, (len(dates) + 1)):
            weekdf, empty = get_weekly_count(i, auth = auth)
            if empty:
                pass
            else:
                github_df = github_df.join(weekdf)
        myrow = github_df.fillna(0).loc[username].tolist()
        for i in range(len(dates)):
            try:
                print('You made %1d comment(s) and %1d reactions to talk %1d.' % (myrow[i*2], myrow[i*2+1], i+1))
            except IndexError:
                pass
    else:
    	print("wrong number of args")


# In[ ]:




