# sample test code to list your google photos albums
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

#SCOPES = 'https://www.googleapis.com/auth/photoslibrary.readonly'
SCOPES = 'https://www.googleapis.com/auth/photoslibrary'
store = file.Storage('credentials.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
    creds = tools.run_flow(flow, store)
service = build('photoslibrary', 'v1', http=creds.authorize(Http()))

results = service.albums().list(
        pageSize=10, fields='nextPageToken,albums(id,title)').execute()
items = results.get('albums', [])
if not items:
    print('No albums found.')
else:
    print('Albums:')
    for item in items:
        print('{} ({})'.format(item['title'].encode('utf-8'), item['id']))
