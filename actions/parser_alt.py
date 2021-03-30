# -*- coding: cp1251 -*-
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from .models import Post
from celery import shared_task

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

    for item in posts:
        if item.find('guid').text not in old_posts_url:
            title = item.find('title').text.replace('[Перевод] ', '')
            url = item.find('guid').text
            categories = ','.join([cat.text for cat in item.findAll('category')])
            date = item.find('pubDate').text.split(',')[1].replace(' GMT', '').lstrip(' ')
            pub_date = datetime.strptime(date, '%d %b %Y %H:%M:%S')
            Post.objects.create(title=title, habr_url=habr_url,  url=url, categories=categories, pub_date=pub_date)
