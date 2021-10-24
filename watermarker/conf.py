# -*- coding: utf-8 -*-

from appconf import AppConf
from django.conf import settings  # pylint: disable=W0611


class WatermarkSettings(AppConf):
    QUALITY = 85
    OBSCURE_ORIGINAL = True
    RANDOM_POSITION_ONCE = True

    class Meta:
        prefix = "watermark"
        holder = "watermarker.conf.settings"
