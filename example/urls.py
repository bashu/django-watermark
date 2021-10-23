import re

from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.views.generic import TemplateView

urlpatterns = [
    url(r"^admin/", admin.site.urls),
]

if settings.SERVE_MEDIA:
    from django.views.static import serve

    urlpatterns += [
        url(
            r"^%s(?P<path>.*)$" % re.escape(settings.STATIC_URL.lstrip("/")),
            serve,
            kwargs={"document_root": settings.STATIC_ROOT},
        )
    ]

    urlpatterns += [
        url(
            r"^%s(?P<path>.*)$" % re.escape(settings.MEDIA_URL.lstrip("/")),
            serve,
            kwargs={"document_root": settings.MEDIA_ROOT},
        )
    ]

urlpatterns += [
    url(r"^$", TemplateView.as_view(template_name="index.html")),
]
