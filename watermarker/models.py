# -*- coding: utf-8 -*-

from django.db import models


class Watermark(models.Model):

    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to='watermarks')
    is_active = models.BooleanField(default=True, blank=True)

    # for inernal use...
    
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name
