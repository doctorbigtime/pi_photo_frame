from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from http.client import HTTPSConnection
from urllib.parse import urlparse

import datetime
import random
import json


def download(url):
    parsed_url = urlparse(url)
    assert parsed_url.scheme == 'https'
    http_cxn = HTTPSConnection(parsed_url.netloc)
    http_cxn.request('GET', parsed_url.path + '?w=640&w=480')
    resp = http_cxn.getresponse()
    assert resp.status == 200
    with open('cache/{}.jpg'.format(picId), 'wb') as f:
        f.write(resp.read())
    http_cxn.close()


SCOPES = 'https://www.googleapis.com/auth/photoslibrary'
store = file.Storage('credentials.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
    creds = tools.run_flow(flow, store)
service = build('photoslibrary', 'v1', http=creds.authorize(Http()))

valid_years = list(range(2015, datetime.datetime.now().year+1))
random_year = random.choice(valid_years)
random_quarter = random.randint(0,3)

start_date = datetime.date(random_year, random_quarter*3 + 1, 1)
end_date   = start_date + datetime.timedelta(days=92)

print('start_date: {}\nend_date: {}\n'.format(start_date, end_date))
filters= {
    'filters': {
        'dateFilter': {
            'ranges': [
                {
                    'startDate': { 'year': start_date.year, 'month': start_date.month, 'day': start_date.day },
                    'endDate': { 'year': end_date.year, 'month': end_date.month, 'day': end_date.day }
                }
            ]
        }
    }
}

search_request = {'pageSize':100,
    'albumId':'AASYawUd1Nq8pgn2hwaO3rPyEIx1N0yazFSCrbSJrbzT6YVsspGJrW8YpW_OiXSa73nPk8azEldL',
}
results = service.mediaItems().search(body=search_request).execute()
num_pics = 0
#while num_pics < 50 and results:
all_pics = []
while results:
    items = results.get('mediaItems', [])
    if not items:
        print('No pictures in this request')
        break
    else:
        for pic in items:
            #url = '{}?w=640&h=480'.format(pic['baseUrl'])
            print('{}'.format(pic))
            all_pics.append({'id': pic['id'], 'url':pic['baseUrl']})
            num_pics = num_pics + 1

    if 'nextPageToken' not in results:
        break
    next_token = results['nextPageToken']
    search_request.update({'pageToken': next_token})
    results = service.mediaItems().search(body=search_request).execute()

with open('picdb.json', 'w') as f:
    json.dump(all_pics, f)

print('There were {} pictures.'.format(num_pics))

