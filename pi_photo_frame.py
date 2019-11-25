# main program. use fbi instead of feh if using framebuffer.
from google_photos import refresh_db, download
import random
import os
import shutil
from dateutil.parser import parse as dtparse
import datetime

num_pics = 50

def add_to_display(pic):
    pic_id = pic['id']
    basename = '{}.jpg'.format(pic_id)
    cache_path = os.path.join('cache', basename)
    if not os.path.exists(cache_path):
        download(pic, cache_path)
        assert os.path.exists(cache_path)
    shutil.copy(cache_path, 'var/')

def clear_display():
    shutil.rmtree('var/', ignore_errors=True)
    os.makedirs('var/')

def display_display():
    os.system('feh -FzZx -B black -D 2 var/')

def main():
    one_month_ago = datetime.date.today() - datetime.timedelta(days=30)
    pics = refresh_db()
    clear_display()
    included = set()
    for key,item in pics.items():
        when = dtparse(item['mediaMetadata']['creationTime'])
        if when.date() >= one_month_ago:
            included.add(key)
            add_to_display(item)
    added = 0
    while added < num_pics:
        random_key = random.choice(list(pics.keys()))
        if random_key in included:
            continue
        add_to_display(pics[random_key])
        added = added + 1
    display_display()


if __name__ == '__main__':
    main()

