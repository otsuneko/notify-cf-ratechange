import os
import psycopg2
import requests
from requests.api import request

# Connect to Heroku PostgreSQL DB
def connect():
    con = psycopg2.connect(os.environ['DATABASE_URL'])
    return con

# Search a record from connected DB
def search_DB(con, sql):
    with con.cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()
    return rows

# Insert a record to DB table
def insert_DB(con, sql, data):
    with con.cursor() as cur:
        cur.execute(sql, data)    
    con.commit()

# Send a notification to LINE
def line_notify(message):
    line_notify_token = os.environ['LINE_NOTIFY_API_KEY']
    line_notify_api = 'https://notify-api.line.me/api/notify'
    payload = {'message': message}
    headers = {'Authorization': 'Bearer ' + line_notify_token}
    requests.post(line_notify_api, data=payload, headers=headers)


# 1. Get Codeforces rate change history
user_name = os.environ['CODEFORCES_USER_NAME']
response = requests.get("https://codeforces.com/api/user.rating?handle=" + user_name)
json_data = response.json()

latest_contest_info = json_data["result"][-1]
contest_id = latest_contest_info["contestId"]
contest_name = latest_contest_info["contestName"]
rank = latest_contest_info["rank"]
rating_update_time_seconds = latest_contest_info["ratingUpdateTimeSeconds"]
old_rating = latest_contest_info["oldRating"]
new_rating = latest_contest_info["newRating"]

# 2. Check if latest contestId exists in DB. If not, insert the record and send the notification with LINE Notify
con = connect()
sql_search_latest_contest_info = "SELECT * FROM contests WHERE contest_id=" + str(contest_id)
res = search_DB(con,sql_search_latest_contest_info)

# If there is an update
if not res:
    # Insert the latest contest info. into DB
    insert_info = (contest_id, contest_name, rank, rating_update_time_seconds, old_rating, new_rating)
    sql_insert_latest_contest_info = "INSERT INTO contests VALUES(%s, %s, %s, %s, %s, %s)"
    insert_DB(con, sql_insert_latest_contest_info, insert_info)

    # send the Notification to LINE
    message = "\n" + user_name + "'s Rank at " + contest_name + " : " + str(rank) + "\n" + "Rating : " + str(old_rating) + "->" + str(new_rating)
    if old_rating < new_rating:
        message += "(+" + str(new_rating-old_rating) + ") :)"
    elif old_rating == new_rating:
        message += "(±0) :|"
    else:
        message += "(" + str(new_rating-old_rating) +") :("
    message += "\n" + "https://codeforces.com/contests/with/" + user_name

    line_notify(message)