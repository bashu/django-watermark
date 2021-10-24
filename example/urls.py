import re

from django.conf import settings
from django.contrib import admin
from django.urls import path, re_path
from django.views.generic import TemplateView

urlpatterns = [
    path("admin/", admin.site.urls),
]

if settings.SERVE_MEDIA:
    from django.views.static import serve

    urlpatterns += [
        re_path(
            r"^%s(?P<path>.*)$" % re.escape(settings.STATIC_URL.lstrip("/")),
            serve,
            kwargs={"document_root": settings.STATIC_ROOT},
        )
    ]

    urlpatterns += [
        re_path(
            r"^%s(?P<path>.*)$" % re.escape(settings.MEDIA_URL.lstrip("/")),
            serve,
            kwargs={"document_root": settings.MEDIA_ROOT},
        )
    ]

urlpatterns += [
    path("", TemplateView.as_view(template_name="index.html")),
]
