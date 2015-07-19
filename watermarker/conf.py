# -*- coding: utf-8 -*-

import warnings

from django.conf import settings  # pylint: disable=W0611

from appconf import AppConf


class WatermarkSettings(AppConf):
    QUALITY = 85
    OBSCURE_ORIGINAL = True
    RANDOM_POSITION_ONCE = True

    class Meta:
        prefix = 'watermark'
        holder = 'watermarker.conf.settings'

    def configure_quality(self, value):
        if getattr(settings, 'WATERMARKING_QUALITY', None):
            warnings.warn("WATERMARKING_QUALITY is deprecated, use WATERMARK_QUALITY", DeprecationWarning)

        return value
