import csv
import requests
from requests.api import request

#Get Codeforces User Info
USER_NAME = "otsuneko"
response = requests.get("https://codeforces.com/api/user.rating?handle=" + USER_NAME)
jsonData = response.json()

#Write Codeforces rate info. to CSV file
with open('codeforces.csv','w', newline='') as f:
    writer = csv.writer(f)
    for contests in jsonData["result"]:
        l = []
        for item in contests.items():
            l.append(item[1])
        writer.writerow(l)