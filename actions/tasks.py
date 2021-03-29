from celery import shared_task
from datetime import timedelta
from .models import Setting, Post
from django.utils import timezone
from .parser_alt import *
from .slackbot import *


def posts_msg_gen(setting):
    posts = Post.objects.filter(pub_date__gte=setting.prev_date())
    if posts:
        msg = ''.join([f'\n<{post.url}|{post.title}>' for post in posts])
        return msg



def date_upd():
    settings = Setting.objects.all()
    for setting in settings:
        date = setting.start_date
        while date < timezone.localtime(timezone.now()):
            date = date + timedelta(minutes=setting.schedule_days)
        setting.start_date = date
        setting.save()


@shared_task
def sender():
    time_start = timezone.now()
    settings = Setting.objects.filter(start_date__lte=timezone.localtime(timezone.now()))

    if settings:
        for setting in settings:
            print(f'setting {setting.name} in progress')
            parser('https://habr.com/ru/rss/company/skillfactory/blog/?fl=ru')
            posts_msg = posts_msg_gen(setting)

            if posts_msg is not None:
                text = f'Привет! У нас есть новости:{posts_msg}'
                channels = setting.channels.split(',')
                for channel in channels:
                    slack_post_msg(text=text, channel=channel)

                setting.start_date = setting.start_date + timedelta(minutes=setting.schedule_days)
                setting.save()
    else:
        print('Not yet!')

    time_finished = timezone.now()
    print(time_finished - time_start)
