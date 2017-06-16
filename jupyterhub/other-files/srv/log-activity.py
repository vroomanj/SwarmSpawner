#!/usr/bin/env python3
"""Log JupyterHub user activity"""
from __future__ import print_function

from datetime import datetime, timedelta
import argparse
import os
import sys
import time

import requests
import sqlite3

from dateutil.parser import parse as parse_date

def scrape_stats(db, host, token, interval):
    r = requests.get('%s/hub/api/users' % host,
        headers={
            'Authorization': 'token %s' % token,
        }
    )
    r.raise_for_status()
    now = datetime.utcnow()
    threshold = now - timedelta(seconds=interval)
    total_active = 0
    total_users = 0
    print(now, end=' ')
    for user in r.json():
        total_users += 1
        name = user['name']
        last_activity = parse_date(user['last_activity'])
        active = bool(user['server'] and last_activity > threshold)
        if active:
            total_active += 1
            if total_active < 10:
                print(name, end=' ')
            elif total_active == 10:
                print('...', end=' ')
        db.execute("INSERT INTO activity VALUES (?, ?, ?)",
            (now, name, active)
        )
    db.commit()
    print("%i/%i active users" % (total_active, total_users))
    sys.stdout.flush()

def init_db(fname):
    db = sqlite3.connect(fname)
    db.execute("""CREATE TABLE IF NOT EXISTS activity (
                date timestamp,
                user text,
                active bool)
                """)
    db.commit()
    return db

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', type=str, default='activity.sqlite',
        help="The sqlite file where activity should be logged.")
    parser.add_argument('--interval', type=int, default=600,
        help="The interval, in seconds, for polling activity. Should be greater than Hub activity interval (5 minutes).")
    parser.add_argument('--hub', type=str, default='http://127.0.0.1:8081',
        help="The hub's url. If no protocol is specified, http will be assumed.")
    opts = parser.parse_args()
    
    try:
        token = os.environ['JPY_API_TOKEN']
    except KeyError:
        print("Need JPY_API_TOKEN env. Create a token with `jupyterhub token [admin_user]`", file=sys.stderr)
        sys.exit(1)
    
    interval = opts.interval
    url = opts.hub
    if '://' not in url:
        url = 'http://' + url
    
    db = init_db(opts.file)
    
    while True:
        scrape_stats(db, url, token, interval)
        time.sleep(interval)
