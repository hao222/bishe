# -*- coding: utf-8 -*-
import django
from .views import get_ueditor_controller

DJANGO_VERSION = django.VERSION[:2]


if DJANGO_VERSION >= (1, 8):
    from django.conf.urls import url
    urlpatterns = [
        url(r'^controller/$', get_ueditor_controller)
    ]

else:
    try:
        from django.conf.urls import patterns, re_path
    except ImportError:
        from django.conf.urls.defaults import patterns, url

    urlpatterns = patterns("",
        re_path(r'^controller/$', get_ueditor_controller)
    )
