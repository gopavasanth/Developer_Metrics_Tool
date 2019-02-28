#!/usr/bin/env python3

import itertools
import json
import os
import requests
import time

from dateutil import relativedelta
from datetime import datetime
from datetime import datetime

def getContributorStats(username, month=None):

    """
    Fetch Gerrit API for patch contributor data.

    Keyword arguments:
    username -- the gerrit handle of the contributor
    month -- the corresponding month to get contributor statistics
    """
    newCount=0;
    Mergedcount=0;
    AbondonedCount=0;
    if month is None:
        date = getCurrentMonth()
    else:
        date = month
    previous_month = decrementMonth(date)
    next_month = incrementMonth(date)

    if username != '':
        link = 'https://gerrit.wikimedia.org/r/changes/?q=owner:'
        url = link + username + '+after:' + \
            previous_month + "+before:" + next_month
        r = requests.get(url)
        jsonArray = r.text
        jsonArray = jsonArray.replace(")]}'", '', 1)
        JArray = json.loads(jsonArray)
        #print(jsonArray)
        for i in JArray:
            if (i['status']=="NEW"):
                newCount = newCount+1
            if (i['status']=="MERGED"):
                Mergedcount = Mergedcount+1
            if (i['status']=="ABANDONED"):
                AbondonedCount = AbondonedCount+1
        print(str(name) +  " Contributions Report")
        print("NEW Patches: " + str(newCount))
        print("MERGED Patches: " + str(Mergedcount))
        print("ABANDONED Patches: " + str(AbondonedCount))
        return json.loads(jsonArray)

def getCurrentMonth(format='%Y-%m'):

    """
    Get current month for a particular year.

    Keyword arguments:
    format -- the current month format to be used
    """

    currentMonth = time.strftime(format)

    return currentMonth

def getContributors(stats, month):

    """
    Get the list of patch contributors.

    Keyword arguments:
    stats -- nested list of all patch contributors
    month -- the month used as the filter
    """
    data = []
    contributors = []
    data = sorted(stats, key=lambda x: x['username'])

    for k, g in itertools.groupby(data, key=lambda x: x['username']):

        contributor_patches = list(g)

        merged_count = abandoned_count = pending_count = 0

        Patch = Query()
        db = getDb()

        merged_count = len(db.search((Patch.status == 'MERGED') & (
            Patch.username == k) & (Patch.created.test(filterMonth, month))))
        abandoned_count = len(db.search((Patch.status == 'ABANDONED') & (
            Patch.username == k) & (Patch.created.test(filterMonth, month))))
        pending_count = len(db.search((Patch.status == 'Needs Review') & (
            Patch.username == k) & (Patch.created.test(filterMonth, month))))

        metrics = {
            "merged_count": merged_count,
            "abandoned_count": abandoned_count,
            "pending_count": pending_count,
            "patch_total": merged_count + abandoned_count + pending_count
        }

        # add metrics to the first child
        contributor_patches[0] = dict(list(metrics.items()) + list(
            contributor_patches[0].items()))
        contributors.append(contributor_patches)  # build list

    # by default sort contributors by patch count, in descending order
    contributors = sorted(contributors, key=lambda x: x[0]['patch_total'],
                          reverse=True)
    print (contributors)
    return contributors

def monthToDate(month):

    """
    Convert month to date format.

    Keyword arguments:
    month -- the month to convert to date format
    """

    month = datetime.strptime(month, ('%Y-%m'))
    date = month.strftime('%Y-%m-%d')  # eg 2018-02-01
    date = datetime.strptime(date, ('%Y-%m-%d'))  # return datetime object
    return date

def incrementMonth(month, n=1):

    """
    Increment date by 'n' months.

    Keyword arguments:
    month -- the current set month
    n -- the number of months to increment (default is 1)
    """

    date = monthToDate(month)
    next_month = date + relativedelta.relativedelta(months=n)
    return next_month.strftime('%Y-%m-%d')

def decrementMonth(month, n=1):

    """
    Decrement date by 'n' months.

    Keyword arguments:
    month -- the current set month
    n -- the number of months to decrement (default is 1)
    """

    date = monthToDate(month)
    previous_month = date - relativedelta.relativedelta(months=n)
    return previous_month.strftime('%Y-%m-%d')

print("Enter the Gerrit username: ")
name=input()
print("Enter the Timeframe in Year-Month (Eg:2018-12) : ")
Timeframe=input()
print("===========================")
#getContributorStats(username=name, month=None)
getContributorStats(username=name, month=Timeframe)
