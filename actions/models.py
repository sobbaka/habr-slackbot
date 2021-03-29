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
class Setting(models.Model):
    name = models.CharField(max_length = 255, unique = True)
    start_date = models.DateTimeField(validators=[only_future])
    schedule_days = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(7)])
    channels = models.CharField(max_length = 255, unique = True)
    def prev_date(self):
        prev_date = self.start_date - datetime.timedelta(minutes=self.schedule_days)
        return prev_date


class Post(models.Model):
    title = models.CharField(max_length = 255, unique = True)
    url = models.SlugField(unique=True)
    habr_url = models.SlugField()
    pub_date = models.DateTimeField()
    categories = models.TextField()

