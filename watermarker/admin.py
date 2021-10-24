# -*- coding: utf-8 -*-

from django.contrib import admin

from .models import Watermark


class WatermarkAdmin(admin.ModelAdmin):
    list_display = ["name", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["name"]


admin.site.register(Watermark, WatermarkAdmin)
