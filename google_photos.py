# list/get pics from album i want.
import os
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from http.client import HTTPSConnection
from urllib.parse import urlparse

import datetime
import random
import json


def download(pic, where):
    from urllib.parse import urlparse
    url = pic['baseUrl']
    pic_id = pic['id']
    parsed_url = urlparse(url)
    assert parsed_url.scheme == 'https'
    http_cxn = HTTPSConnection(parsed_url.netloc)
    http_cxn.request('GET', parsed_url.path + '?w=640&w=480')
    resp = http_cxn.getresponse()
    assert resp.status == 200, 'failed to download: {}?w=640&w=480 resp: {}'.format(parsed_url.geturl(), resp.status)
    with open('{}'.format(where), 'wb') as f:
        f.write(resp.read())
    http_cxn.close()


def load_db():
    if os.path.exists('db.json'):
        with open('db.json', 'r') as f:
            db = json.load(f)
    else:
        db = {}
    print("Loaded {} pics.".format(len(db.keys())))
    return db


def refresh_db(progress_cb=None):
    print_it = lambda num_pics: print('Processed {} pics    '.format(num_pics), end='\r')
    progress_cb = progress_cb or print_it
    SCOPES = 'https://www.googleapis.com/auth/photoslibrary.readonly'
    store = file.Storage('credentials.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('photoslibrary', 'v1', http=creds.authorize(Http()))
    #pics = load_db()
    pics = {}
    with open('secrets.json', 'r') as f:
        secrets = json.load(f)
    albumId = secrets['pi_photo_frame']['albumId']

    search_request = {'pageSize':100,
        'albumId': albumId,
    }
    results = service.mediaItems().search(body=search_request).execute()
    num_pics = 0
    new_pics = {}
    done = False
    while not done:
        items = results.get('mediaItems', [])
        if not items:
            print('No pictures in this request')
            break
        else:
            for pic in items:
                if pic['id'] in pics:
                    print("Already know about {}".format(pic['id']))
                    done = True
                    break
                if not 'image' in pic['mimeType']:
                    continue
                num_pics = num_pics + 1
                progress_cb(num_pics)

                new_pics[pic['id']] = pic

        if 'nextPageToken' not in results:
            break
        next_token = results['nextPageToken']
        search_request.update({'pageToken': next_token})
        results = service.mediaItems().search(body=search_request).execute()

    print("Found {} new pics.".format(len(new_pics)))
    if len(new_pics) > 0:
        pics.update(new_pics)
        print("Total: {} pics.".format(len(pics)))

        with open('db.json.new', 'w') as f:
            json.dump(pics, f, indent=2)
        os.replace('db.json.new', 'db.json')
    return pics

