import random, datetime, requests, json




temp_data = {'stu_num' : 20150597}
data = json.dumps(temp_data)
url = 'http://skyhigh00v.ddns.net:5555/dbtest'
response = requests.post(url, data = data)
result = json.loads(response.text)
for idx in result:
    print(idx)
