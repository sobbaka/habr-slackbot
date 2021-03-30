from celery import shared_task
from datetime import timedelta
from .models import Setting, Post
from django.utils import timezone
from .parser_alt import *
from .slackbot import *


def posts_msg_gen(setting):
    tags = setting.tags.split(',') if setting.tags else None
    posts = Post.objects.filter(pub_date__gte=setting.prev_date()).order_by('pub_date')
    if posts:
        if tags:
            posts = set([post for tag in tags for post in posts if tag.lstrip().lower() in post.categories.lower()])
        msg = ''.join([f'\n<{post.url}|{post.title}>' for post in posts])
        return msg


def setting_date_upd():
    settings = Setting.objects.all()
    for setting in settings:
        date = setting.start_date
        while date < timezone.localtime(timezone.now()):
            date = date + timedelta(days=setting.schedule_days, hours=setting.schedule_hours)
        setting.start_date = date
        setting.save()


@shared_task
def sender():
    settings = Setting.objects.filter(start_date__lte=timezone.localtime(timezone.now()))
    if settings:
        for setting in settings:
            posts_msg = posts_msg_gen(setting)
            if posts_msg is not None:
                text = f'{setting.greeting_text}{posts_msg}'
                channels = setting.channels.split(',')
                for channel in channels:
                    slack_post_msg(text=text, channel=channel)
                setting.start_date = setting.start_date + timedelta(days=setting.schedule_days, hours=setting.schedule_hours)
                setting.save()
