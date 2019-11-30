# main program. use fbi instead of feh if using framebuffer.
from google_photos import refresh_db, load_db, download
import random
import os
import shutil
from dateutil.parser import parse as dtparse
import datetime
import pygame

num_pics = 50
screen = None
font = None

def update_status(msg):
    global screen
    global font
    text = font.render(msg, True, (255,255,255))
    rect = text.get_rect(center=(screen.get_width()/2, screen.get_height()/2))
    pygame.draw.rect(screen, (0,0,0), pygame.Rect(0,rect.y,screen.get_width(),rect.height))
    screen.blit(text, rect)
    pygame.display.update()

progress_count = 0
def start_progress(msg, count):
    global progress_count
    global screen
    global font
    progress_count = count
    pygame.draw.rect(screen, (0,0,0), pygame.Rect(10,10,screen.get_width() - 20, 30))
    pygame.draw.rect(screen, (0,255,0), pygame.Rect(10,10,screen.get_width() - 20, 30), 2)
    pygame.draw.rect(screen, (0,0,0), pygame.Rect(0, 50, screen.get_width(), 50))
    text = font.render('0%', True, (255,255,255))
    screen.blit(text, text.get_rect(center=(screen.get_width()/2, 90)))
    update_status(msg)

def update_progress(current_count):
    global progress_count
    global screen
    global font
    pct = float(current_count)/progress_count
    pygame.draw.rect(screen, (100,255,100), pygame.Rect(12,12,int((screen.get_width()-24)*pct), 27))
    pygame.draw.rect(screen, (0,0,0), pygame.Rect(0, 50, screen.get_width(), 50))
    text = font.render('{}%'.format(int(pct*100)), True, (255,255,255))
    rect = text.get_rect(center=(screen.get_width()/2, 90))
    screen.blit(text, rect)
    pygame.display.update()

def add_to_display(pic):
    pic_id = pic['id']
    basename = '{}.jpg'.format(pic_id)
    cache_path = os.path.join('cache', basename)
    if not os.path.exists(cache_path):
        download(pic, cache_path)
        assert os.path.exists(cache_path)
    shutil.copy(cache_path, 'var/')

def clear_display():
    update_status('Clearing display')
    shutil.rmtree('var/', ignore_errors=True)
    os.makedirs('var/')

def display_images():
    os.system('feh -FzZx -B black -D 2 var/')

def progress_cb(num_dl):
    update_status('{} pictures loaded.'.format(num_dl))

def main():
    global screen
    global font
    pygame.init()
    # TODO: use display info
    # display_info = pygame.display.info()
    screen = pygame.display.set_mode((320,240))
    font = pygame.font.Font(None, 40)
    now = datetime.datetime.now()
    today = now.date()
    one_month_ago = today - datetime.timedelta(days=30)
    if os.path.exists('db.json') and now.timestamp() - os.stat('db.json').st_mtime  < 3000:
        pics = load_db()
    else:
        pics = refresh_db(progress_cb)
    clear_display()
    included = set()
    start_progress('Adding recent pictures', len(pics))
    for i, (key,item) in enumerate(pics.items()):
        when = dtparse(item['mediaMetadata']['creationTime'])
        if when.date() >= one_month_ago:
            included.add(key)
            add_to_display(item)
        update_progress(i)
    added = 0
    start_progress('Adding random pictures', num_pics)
    while added < num_pics:
        random_key = random.choice(list(pics.keys()))
        if random_key in included:
            continue
        add_to_display(pics[random_key])
        added = added + 1
        update_progress(added)
    pygame.display.quit()
    display_images()


if __name__ == '__main__':
    main()

