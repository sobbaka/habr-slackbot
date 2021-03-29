# -*- coding: cp1251 -*-
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from .models import Post

def get_html(url):
    r = requests.get(url)
    return r.text

def parser(habr_url):
    html = get_html(habr_url)
    soup = BeautifulSoup(html, 'xml')
    posts = soup.findAll('item')

    for item in posts:
        if not Post.objects.filter(url = item.find('guid').text):
            title = item.find('title').text.replace('[Перевод] ', '')
            url = item.find('guid').text
            categories = [cat.text for cat in item.findAll('category')]
            date = item.find('pubDate').text.split(',')[1].replace(' GMT', '').lstrip(' ')
            pub_date = datetime.strptime(date, '%d %b %Y %H:%M:%S')
            Post.objects.create(title=title, habr_url=habr_url,  url=url, categories=categories, pub_date=pub_date)
