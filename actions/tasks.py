import requests
from django.utils import timezone
from celery import shared_task
from bs4 import BeautifulSoup
from datetime import timedelta, datetime

from .models import Setting, Post
from .slackbot import *

# Slack message generator
def posts_msg_gen(setting):
    tags = setting.tags.split(',') if setting.tags else None
    if setting.first_launch:
        posts = Post.objects.order_by('-pub_date')
    elif setting.send_every_new_post:
        post = Post.objects.order_by('-pub_date')[0] #change ti POST ID-PK
        if tags:
            msg = f'\n<{post.url}|{post.title}>' \
                if any(True for tag in tags if tag in tag.lstrip().lower() in post.categories.lower()) else None
        else:
            msg = f'\n<{post.url}|{post.title}>'
        return msg
    else:
        posts = Post.objects.filter(pub_date__gte=setting.prev_date()).order_by('-pub_date')
    if posts:
        if tags:
            posts = list(set([post for tag in tags for post in posts if tag.lstrip().lower() in post.categories.lower()]))
        posts = posts[:5] if len(posts) > 5 and setting.first_launch else posts
        msg = ''.join([f'\n<{post.url}|{post.title}>' for post in posts])
        setting.first_launch = False
        setting.save()
        return msg

# Bot settings date updater. Date must be always in Future.
# If something happend to task manager you can always update dates before next launch
def setting_date_upd():
    settings = Setting.objects.all()
    for setting in settings:
        date = setting.start_date
        while date < timezone.localtime(timezone.now()):
            date = date + timedelta(days=setting.schedule_days, hours=setting.schedule_hours)
        setting.start_date = date
        setting.save()


def sender(settings):
    for setting in settings:
        posts_msg = posts_msg_gen(setting)
        if posts_msg is not None:
            text = f'{setting.greeting_text}{posts_msg}'
            tokens = setting.token.all()
            channels = setting.channels.split(',')
            for token in tokens:
                for channel in channels:
                    slack_post_msg(text=text, token=token.token, channel=channel)

            if setting.debug:
                setting.start_date = setting.start_date + timedelta(minutes=setting.schedule_hours)
            else:
                setting.start_date = setting.start_date + timedelta(days=setting.schedule_days,
                                                                hours=setting.schedule_hours)
            setting.save()

@shared_task
def schedule_sender():
    settings = Setting.objects.filter(start_date__lte=timezone.localtime(timezone.now()), send_every_new_post=False)
    if settings:
        sender(settings)


# Habr parser part
HABR_URL = 'https://habr.com/ru/rss/company/skillfactory/blog/?fl=ru'

def get_html(url):
    r = requests.get(url)
    return r.text

@shared_task
def parser():
    habr_url = HABR_URL
    html = get_html(habr_url)
    soup = BeautifulSoup(html, 'xml')
    posts = soup.findAll('item')
    old_posts_url = Post.objects.values_list('url', flat=True)
    settings = Setting.objects.filter(send_every_new_post=True)

    for item in posts:
        if item.find('guid').text not in old_posts_url:
            title = item.find('title').text.replace('[Перевод] ', '')
            url = item.find('guid').text
            categories = ','.join([cat.text for cat in item.findAll('category')])
            date = item.find('pubDate').text.split(',')[1].replace(' GMT', '').lstrip(' ')
            pub_date = datetime.strptime(date, '%d %b %Y %H:%M:%S')
            Post.objects.create(title=title, habr_url=habr_url,  url=url, categories=categories, pub_date=pub_date)

            if settings:
                sender(settings)