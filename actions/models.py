from django.db import models
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
import datetime

def only_future(value):
    now = timezone.now()
    if value <= now:
        raise ValidationError('Date cannot be in the past.')

# Create your models here.
class Workspace(models.Model):
    """This is setting for Slack Workplace"""
    name = models.CharField(max_length=255, verbose_name='Название')
    token = models.CharField(max_length=255, verbose_name='Token')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Настройка Workspace'
        verbose_name_plural = 'Настройки Workspace'


class Setting(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name = 'Название')
    greeting_text = models.TextField(verbose_name='Текст приветствия')
    start_date = models.DateTimeField(
        validators=[only_future],
        verbose_name='Следующая рассылка',
        help_text='Можно указать только будущее время по МСК')
    schedule_days = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(7)],
        verbose_name = 'Периодичность Дни',
    )
    schedule_hours = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Периодичность Часы',
        help_text='Оставьте поля пустыми для отправки каждого нового поста на канале'
    )
    channels = models.CharField(
        max_length=255,
        verbose_name='Каналы',
        help_text='Укажите названия каналов через запятую #general, #random'
    )
    tags = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Ключевые слова',
        help_text='Укажите названия каналов через запятую математика, python'
    )
    token = models.ManyToManyField(Workspace, related_name='settings')
    first_launch = models.BooleanField(
        default=True,
        verbose_name='Первый запуск',
        help_text='При первом запуске делает рассылку первых 5 постов подходящих под условия настройки. Далее согласно настройке'
    )
    debug = models.BooleanField(default=False)
    send_every_new_post = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        time = self.schedule_hours + self.schedule_days
        if not time:
            self.send_every_new_post = True
        super(Setting, self).save(*args, **kwargs)


    def prev_date(self):
        """Getter for date of previous mailing"""
        prev_date = self.start_date - datetime.timedelta(days=self.schedule_days, hours=self.schedule_hours)
        return prev_date

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Настройка'
        verbose_name_plural = 'Настройки'


class Post(models.Model):
    title = models.CharField(max_length = 255, unique = True)
    url = models.SlugField(unique=True, max_length = 255)
    habr_url = models.SlugField(max_length = 255)
    pub_date = models.DateTimeField()
    categories = models.TextField()

    def __str__(self):
        return f"{self.title[:30]} {self.pub_date.strftime('%d-%m-%y-%H-%m')}"
