#-*-coding:utf-8-*-
from . import views
from django.urls import path,re_path

app_name = "design"
urlpatterns = [
    path("login/",views.login,name="login"),
    # path("login_check/",views.login_check,name="login_check"),
    path("log_out/",views.log_out,name="log_out"),
    path("register/",views.register,name="register"),
    path("register_check/",views.register_check,name="register_check"),
    path("forget_pwd/",views.forget_pwd,name="forget_pwd"),

    path("code/",views.code,name="code"),
    path('user_check/',views.user_check,name="user_check"),
    path('phone_check/',views.phone_check,name="phone_check"),
    path("re_pwd/",views.repwd,name="repwd"),
    path("",views.home,name='home'),
    path("about/",views.about,name='about'),
    re_path(r'^article/(?P<c_id>[0-9]*)$',views.article,name='article'),
    path('connect/',views.connect,name='connect'),
    re_path(r'^detail/(?P<aid>\d+)/$',views.detail,name='detail'),
    path('publish/',views.publish,name='publish'),
    path('people/',views.people,name='people'),
    path('score/',views.score,name='score'),
    path('mypub/<int:status>',views.mypub,name='mypub'),
    path('message/',views.message,name='message'),
    path('ajax_upimg/',views.ajax_upimg,name='ajax_upimg'),
    path('duihuan/',views.duihuan,name='duihuan'),
    # path('ajax_duihuan/',views.ajax_duihuan,name='ajax_duihuan'),
    re_path(r'^article_search/(?P<c_id>[0-9]*)$',views.article_search,name='article_search'),
    # path('article_search/',views.article_search,name='article_search')
    re_path(r"^comment/(?P<pk>\d+)/$", views.article_comment, name='article_comment'),
    path('zan/',views.ajax_zan,name='ajax_zan'),
    path('fen/',views.ajax_fen,name='ajax_fen'),
]