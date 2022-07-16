from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from datetime import datetime



class User(AbstractUser):
    phone = models.TextField(_('Телефон'),blank=True,default=542)
    email = models.EmailField(_('Почта'),blank=True)
    score = models.IntegerField(_('Рейтинг'),blank=True,default=542)

    class Meta(AbstractUser.Meta):
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
