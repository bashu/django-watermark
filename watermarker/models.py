# -*- coding: utf-8 -*-

from django.core.cache import caches
from django.db import models
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible

from watermarker.conf import settings

CACHE_BACKEND_NAME = settings.WATERMARK_CACHE_BACKEND_NAME


@python_2_unicode_compatible
class Watermark(models.Model):

    name = models.CharField(
        max_length=50, verbose_name=_("name"))
    image = models.ImageField(
        upload_to='watermarks', verbose_name=_("image"))
    is_active = models.BooleanField(
        default=True, blank=True, verbose_name=_("is active"))

    # for internal use...

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = _("watermark")
        verbose_name_plural = _("watermarks")

    def __str__(self):
        return self.name


@receiver(post_save, sender=Watermark)
@receiver(pre_delete, sender=Watermark)
def delete_watermark_cache_name(sender, instance, created=False, **kwargs):
    """
    Pre-delete and Post_save signal.
    """
    cache = caches[CACHE_BACKEND_NAME] if CACHE_BACKEND_NAME else None
    # use defined cache backend
    if cache:
        cache.delete('watermark_%s' % (instance.name))
