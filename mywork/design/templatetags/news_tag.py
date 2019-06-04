#-*-coding:utf-8-*-
from django.db.models import Q

from ..models import *
from django import template
from django.db.models.aggregates import Count,Max
from datetime import datetime

register = template.Library()

#经典案例
@register.simple_tag
def get_class_article(num=6):
    return Article.objects.filter(Q(view_count__gte=5),Q(votes_count__gte=5))[:num]

#热度最高
@register.simple_tag
def get_view_article(num=8):
    return Article.objects.all().order_by('view_count')[:num]


@register.simple_tag
def get_vip_article(num=6):
    return Article.objects.all().order_by('votes_count')[:num]

@register.simple_tag
def get_money_article(num=6):
    return Article.objects.filter(source__contains='人民日报').order_by('id')[:num]

#最新
@register.simple_tag
def get_recent1_art(num=1):
    return Article.objects.all().order_by('-distribute_date')[:num]

#最新发布
@register.simple_tag
def get_recent_art(num=4):
    return Article.objects.all().order_by('-distribute_date')[:num]
@register.simple_tag
def get_recents_art(num=5):
    return Article.objects.filter(status=1).order_by('-distribute_date')[:num]

#vip >=3
@register.simple_tag
def max_ok(num=2):
    return Article.objects.filter(author__vip__gte=3)[:2]


# 过滤器  时间 几分钟
@register.filter(name='cut')
def cut(value):
    date1 = datetime.now().timestamp()
    date2 = value.timestamp()
    date = date1-date2
    if date>60 and date/60<60:
        return str(round(date/60)) +"分钟前"
    elif date/60>60 and date/3600<24:
        return str(round(date/3600))+'小时前'
    elif date/3600>24 and date/3600/24<30:
        return str(round(date/3600/24))+"天前"
    elif date/3600/24>30 and date/3600/24/30<12:
        return str(round(date/3600/24/30))+"月前"
    else:
        return "刚刚"

