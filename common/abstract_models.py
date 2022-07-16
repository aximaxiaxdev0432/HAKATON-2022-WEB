from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _


class BaseActive(models.Model):
    active = models.BooleanField(
        _("Активен"),
        default=True
    )

    class Meta:
        abstract = True


class BaseDateTime(models.Model):
    created_dt = models.DateTimeField(
        _("Дата создания"),
        auto_now_add=True
    )
    updated_dt = models.DateTimeField(
        _("Дата обновления"),
        auto_now=True
    )

    class Meta:
        abstract = True


