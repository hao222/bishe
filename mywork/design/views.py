import datetime

from django.contrib.auth import logout
from django.contrib import messages
from django.db import connection
from django.db.models import Q
from django.shortcuts import render,redirect,get_object_or_404,HttpResponseRedirect
from django.http import HttpResponse,JsonResponse
from django.template import loader
from django.urls import reverse

from .models  import *
import json,re,os
from mywork import settings
from .forms import *
import urllib
import urllib.request
import hashlib
from django.views.decorators.csrf import csrf_exempt
from random import randint
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
import base64
# Create your views here.

#md5加密
def md5(args):
    m = hashlib.md5()
    m.update(args.encode('utf-8'))
    return m.hexdigest()


# 短信验证
@csrf_exempt
def code(request):
    statusStr = {
        '0': '短信发送成功',
        '-1': '参数不全',
        '-2': '服务器空间不支持,请确定支持curl或者fsocket,联系您的空间商解决或者更换空间',
        '30': '密码错误',
        '40': '账号不存在',
        '41': '余额不足',
        '42': '账户已过期',
        '43': 'IP地址限制',
        '50': '内容含有敏感词',
    }

    smsapi = 'http://api.smsbao.com/'
    # 短信平台账号
    user = 'wuhao11'
    # 短信平台密码
    password = md5('wuhao11')
    code = randint(1000,10000)
    # 要发送的短信内容
    content = '谢谢你注册非凡公司,你此次的验证码为:'+str(code)+'请在60秒内接收'
    # 要发送的短信内容
    phone = request.POST['phone']
    data = urllib.parse.urlencode({'u': user, 'p': password, 'm': phone, 'c': content})
    send_url = smsapi + 'sms?' + data

    response = urllib.request.urlopen(send_url)
    the_page = response.read().decode('utf-8')
    request.session['code'] = code
    print(statusStr[the_page])
    data_dict = {
        'status_code': the_page,
        'status_text': statusStr[the_page],
        'yzm': code
    }
    print(data_dict)
    return JsonResponse(data_dict)


phone_reg = re.compile(r'^(13\d|14[5|7]|15\d|166|17[3|6|7]|18\d)\d{8}$')
pwd_reg = re.compile(r"^[\w]{6,12}$")

#登录
# def login(request):
#     username = request.get_signed_cookie('username', salt='aaa', default=False)
#     password = request.get_signed_cookie('password', salt='aaa', default=False)
#     return render(request, 'mywork/login.html', locals())
#登录验证
def login(request):
    user = request.session.get("username")
    checked = request.session.get('check', False)
    if request.method == "POST":
        username1 = request.POST['username']
        password1 = request.POST['password']
        if not username1:
            return render(request, 'mywork/login.html', {'msg': "用户名不能为空"})
        if not password1:
            return render(request, 'mywork/login.html', {'msg': "密码不能为空"})
        user = Users.objects.filter(username=username1)
        if user.exists():
            pwd = md5(password1)
            pwd1 = user[0].password
            if pwd1 == pwd:
                check = request.POST.get('rember')
                if check == 'on':
                    request.session['check'] = 'check'
                    request.session['username'] = username1
                    request.session['password'] = password1
                else:
                    request.session.flush()
                msg = "登录成功!"
                user1 = Users.objects.get(username=username1)
                request.session['username'] = username1
                # return render(request,'mywork/home.html',locals())
                return HttpResponseRedirect(reverse('design:home',args=()))
            else:
                msg = "密码输入错误"
                return render(request, 'mywork/login.html', locals())
        else:
            msg = "用户名不存在"
    else:
        if checked != False:
            username = request.session.get('username')
            password = request.session.get("password")
        else:
            request.session.flush()
    return render(request, 'mywork/login.html', locals())


#退出登录
def log_out(request):
    if not request.session.get('username', False):
        return render(request, 'mywork/login.html')
    else:
        request.session.flush()
    return redirect('design:login')

#注册
def register(request):
    return render(request,'mywork/register.html')

#注册验证
def register_check(request):
    if request.method == 'POST':
            username = request.POST['username']
            code = request.POST['code']
            if not username:
                return render(request, 'mywork/register.html', {'msg': "用户名不能为空"})
            else:
                if Users.objects.filter(username=username):
                    return render(request,'mywork/register.html',{"msg":"*用户名已存在!"})
                else:
                    phone = request.POST['phone']
                    if not phone:
                        return render(request, 'mywork/register.html', {'msg': "手机号不能为空"})
                    else:
                        rephone = re.match(phone_reg, phone)
                        if rephone:
                            if Users.objects.filter(phone=phone):
                                return render(request,"mywork/register.html",{"msg":"*手机已经注册!"})
                            else:
                                codes = request.session['code']

                                if str(code) == str(codes):
                                    password1 = request.POST['pwd']
                                    if not password1:
                                        return render(request, 'mywork/register.html', {'msg': "密码不能为空"})
                                    else:
                                        repassword = re.match(pwd_reg, password1)
                                        if repassword:
                                            repwd = request.POST['rpwd']
                                            if password1 == repwd:
                                                password = md5(password1)
                                                author = Users(username=username,phone=phone,password=password)
                                                author.save()
                                                request.session['username'] = username
                                                return render(request,'mywork/login.html',{"msg":"恭喜你注册成功!"})
                                            else:
                                                username = request.POST['username']
                                                phone = request.POST['phone']
                                                password = request.POST['rpwd']
                                                msg = "*俩次密码不一致"
                                                return render(request,'mywork/register.html',locals())
                                        else:
                                            username = request.POST['username']
                                            phone = request.POST['phone']
                                            msg = "*密码格式不对,重新输入"
                                            return render(request,'mywork/register.html',locals())
                                else:
                                    username = request.POST['username']
                                    phone = request.POST['phone']
                                    msg = "*验证码不对,请重新输入"
                                    return render(request,'mywork/register.html',locals())
                        else:
                            username = request.POST['username']
                            msg = "*手机号格式不正确,重新输入"
                            return render(request,'mywork/register.html',locals())
    return render(request,'mywork/register.html',locals())


#忘记密码找回
def forget_pwd(request):
    if request.method == "POST":
        phone = request.POST.get('phone')
        codes = request.session['code']
        code = request.POST.get('code')
        if Users.objects.filter(phone=phone).exists():
            user = Users.objects.get(phone=phone)
            if str(code) == str(codes):
                return render(request,'mywork/repwd.html', locals())
            else:
                return render(request,'mywork/forget.html',{'msg':'验证码错误.'})
        else:
            return render(request,'mywork/forget.html',{'msg':'没有此用户'})
    return render(request,'mywork/forget.html',locals())


def repwd(request):
    if  request.method == "POST":
        user_id = request.POST['hidden']
        user = Users.objects.get(id=user_id)
        pwd = request.POST['pwd']
        rewpd = request.POST['rpwd']
        if rewpd == pwd:
            password = md5(pwd)
            user.password = password
            user.save()
            msg = '修改密码成功'
            return render(request, 'mywork/login.html', locals())
        else:
            return render(request, 'mywork/login.html',{"msg":"密码不一致"})
    return HttpResponse("非法入侵!")

def a(request):
    return render(request,'mywork/repwd.html')


#用户名检测
def user_check(request):
    if request.method == 'GET':
        username = request.GET.get('username',False)
        if Users.objects.filter(username=username).exists():
            return JsonResponse({'status':0,"msg":'用户存在'})
        else:
            return JsonResponse({'status':1,'msg':'可以使用'})
    else:
        return JsonResponse({'status':2,"msg":'非法'})

#手机号检测
def phone_check(request):
    if request.method == 'GET':
        phone = request.GET.get('phone',False)
        if Users.objects.filter(phone=phone).exists():
            return JsonResponse({'status':0,"msg":'手机号已存在'})
        else:
            return JsonResponse({'status':1,'msg':'可以使用'})
    else:
        return JsonResponse({'status':2,"msg":'非法'})

#-----------------------主页  home ---------------------------
def home(request):
    user1 = request.session.get("username", False)
    if user1 !=False:
        user1 = Users.objects.get(username=user1)
    return render(request,'mywork/home.html',locals())

#---------------------关于我们-------------------------------
def about(request):
    user1 = request.session.get("username", False)
    if user1 != False:
        user1 = Users.objects.get(username=user1)
    return render(request,'mywork/about.html',locals())

#--------------------article 经典案例--- ---------------------
def article(request,c_id=None):
    category_list = Sort.objects.all()
    user1 = request.session.get("username", False)
    if user1 != False:
        user1 = Users.objects.get(username=user1)
    if c_id=="":
        articles = Article.objects.filter(status=1)
    else:
        if Sort.objects.filter(id=c_id) :
            category = Sort.objects.get(id=c_id)
            articles = category.categorys.filter(status=1)
    paginator = Paginator(articles,3)
    if request.method == 'POST':
        page = request.POST['tt']
    else:
        page = request.GET.get('page')
    try:
        customer = paginator.page(page)
    except PageNotAnInteger:
        customer = paginator.page(paginator.num_pages)
    except EmptyPage:
        customer = paginator.page(paginator.num_pages)
    articles = customer
    return render(request,'mywork/blog.html',locals())

#--------------------connect 联系我们------------------------
def connect(request):
    user1 = request.session.get("username", False)
    
    if user1 != False:
        user1 = Users.objects.get(username=user1)
        # if not request.COOKIES.get('user%s',user1):
            
        if request.method == 'POST':
            cname = user1
            cphone = request.POST.get('phone')
            cqq = request.POST.get('qie')
            cmessage = request.POST.get('content')
            reliseus = ConnectUser()
            reliseus.name = cname
            reliseus.phone = cphone
            reliseus.QQ = cqq
            reliseus.message = cmessage
            reliseus.save()
            messages.info(request,'留言成功,请稍后...')
                
        # else:
        #     messages.info(request,'留言次数过多,请明天再留言~~')
    else:
        messages.info(request,'有账号后方可留言~~')
    # 存个cookie 限制一下在一定时间内不让再次提交
    response = render(request, 'mywork/contact.html', locals())
    response.set_cookie('user%s' % user1,'true')

    return response

#----------------------案例搜索---------------------------------
def article_search(request,c_id=None):
    category_list = Sort.objects.all()
    user1 = request.session.get("username", False)
    if user1 != False:
        user1 = Users.objects.get(username=user1)
    title = request.GET.get('qq','')
    if title is None or title == "":
        articles = Article.objects.filter(status=1)
    else:
        if not title.isdigit():
            articles = Article.objects.filter(status=1, title__contains=title)
        else:
            articles = Article.objects.filter(status=1,id=title)
    paginator = Paginator(articles, 3)
    if request.method == 'POST':
        page = request.POST['tt']
    else:
        page = request.GET.get('page')
    try:
        customer = paginator.page(page)
    except PageNotAnInteger:
        customer = paginator.page(paginator.num_pages)
    except EmptyPage:
        customer = paginator.page(paginator.num_pages)
    articles = customer
    return render(request, 'mywork/blog.html', locals())
#---------------------文章详情  --------------------------------

def detail(request,aid):
    category_list = Sort.objects.all()
    article = get_object_or_404(Article, id=aid)
    articles = Article.objects.filter(id=aid)
    # if article.status==1:
    #     article=article

    if  not request.COOKIES.get('article_%s_readed' % aid):
        article.view_count +=1
        article.save()
    comment_list = Comment.objects.filter(article=article).order_by('-send_time')
    user1 = request.session.get("username", False)
    if user1 != False:
        user1 = Users.objects.get(username=user1)
    paginator = Paginator(comment_list, 3)
    page = request.GET.get('page')
    try:
        customer = paginator.page(page)
    except PageNotAnInteger:
        customer = paginator.page(paginator.num_pages)
    except EmptyPage:
        customer = paginator.page(paginator.num_pages)
    comment_list = customer
    response = render(request,'mywork/blog-inner.html',locals())
    response.set_cookie('article_%s_readed' % aid,'true')
    return response

#-----------------------评论文章------------------------------
def article_comment(request,pk):
    user1 = request.session.get("username", False)
    if user1 != False:
        user1 = Users.objects.get(username=user1)
    article = get_object_or_404(Article, pk=pk)
    if request.method == 'POST':
        article = article
        # user = request.POST['user']
        if not Users.objects.filter(username=user1):
            msg = '请先登录再评论~'
            return render(request, 'mywork/blog-inner.html', locals())
        else:
            content = request.POST['content']
            comment = Comment(article=article, content=content, user=Users.objects.get(username=user1))
            comment.save()
            messages.info(request,'发表成功')
            return HttpResponseRedirect(reverse('design:detail',args=(pk,)))
    else:

        return render(request, 'mywork/blog-inner.html', locals())

#--------------------------------z点赞-----------------------
@csrf_exempt
def ajax_zan(request):
    a_id = request.GET.get('aid')
    article = get_object_or_404(Article, id=a_id)
    user1 = request.session.get("username", False)
    if user1 !=False:
        user1 = Users.objects.get(username=user1)
        if Likes.objects.filter(author=user1) and Likes.objects.filter(article=article):
            msg = '已经点过赞,不要重复点赞'
            return JsonResponse({'status':'0','msg':msg})
        else:
            like = Likes()
            like.author = user1
            like.article=article
            like.save()
            article.votes_count +=1
            article.save()
            votes = article.votes_count
            msg = '点赞成功'
            return JsonResponse({'status':'1','msg':msg,'votes':votes})
    else:
        msg = '请先登录'
        return JsonResponse({'status':'2','msg':msg})

#---------------------------分享---------------------------
@csrf_exempt
def ajax_fen(request):
    a_id = request.GET.get('aid')
    article = get_object_or_404(Article, id=a_id)
    user1 = request.session.get("username", False)
    if user1 != False:
        user1 = Users.objects.get(username=user1)
        if Share.objects.filter(author=user1) and Share.objects.filter(article=article):
            msg = '已经分享过,不要重复分享'
            return JsonResponse({'status':'0','msg':msg})
        else:
            share = Share()
            share.author = user1
            share.article=article
            share.save()
            article.share_count +=1
            article.save()
            share_count = article.share_count
            bill = Bill()
            bill.title = "分享策划"
            bill.author = user1
            bill.save()
            user1.score +=100
            user1.save()
            msg = '分享成功'
            return JsonResponse({'status':'1','msg':msg,'share_count':share_count})
    else:
        msg = '请先登录~'
        return JsonResponse({"status":'2','msg':msg})

#---------------------个人信息-------------------------------
def people(request):
    user1 = request.session.get("username", False)
    if user1 != False:
        user1 = Users.objects.get(username=user1)
        if request.method== 'POST':
            form = PeopleForm(request.POST, instance=user1)
            if form.is_valid():
                phone = form.cleaned_data['phone']
                rephone = re.match(phone_reg,phone)
                if rephone:
                    if rephone !=user1.phone:
                        form.save()
                        msg='修改成功'
                        return render(request,'mywork/people.html',locals())
                    else:
                        msg = '手机号已被注册'
                        return render(request, 'mywork/people.html', locals())
                else:
                    msg = "手机格式不对"
                    return render(request, 'mywork/people.html', locals())
            else:
                msg = "提交内容不合法"
                return render(request, 'mywork/people.html', locals())
        form = PeopleForm(instance=user1)
        return render(request, 'mywork/people.html', locals())
    return HttpResponse("非法入侵")

#--------------------头像裁剪--------------------------------
@csrf_exempt
def ajax_upimg(request):
    user = request.session.get('username')
    user = Users.objects.get(username=user)
    if request.method == "POST":
        img_file = request.POST['file']
        img_list = img_file.split(',')
        type = img_list[0].split('/')[1].split(';')[0]
        data_str = base64.b64decode(img_list[1])
        a = str(user.id)
        db_path = a + "." + type
        user.photo = db_path
        print(os.path)
        if os.path.exists('media/'+ db_path):
            os.remove('media/'+ db_path)
        with open('media/'+db_path, 'wb+') as destination:
            destination.write(data_str)
            user.save()
            return JsonResponse({'status': '1', 'path': db_path})
    return JsonResponse({'status': '0', 'path': ''})
#-------------------发布策划--------------------------------
def publish(request):
    user1 = request.session.get("username", False)
    categories = Sort.objects.all()
    if user1 != False:
        user1 = Users.objects.get(username=user1)
        if user1.leave_count > 0:
            if request.method == 'POST':
                content = request.POST.get('contentx')
                category_id = request.POST.get('category_id')
                post = request.POST.copy()
                post['category'] = category_id
                post['author'] = user1.id
                form=ArticleForm(post,request.FILES)

                if form.is_valid():
                    form.save()
                    article = Article.objects.last()
                    article.content =content
                    article.save()
                    user1.leave_count -=1
                    user1.save()
                    messages.info(request,'提交成功')
                    return redirect('design:publish')
                else:
                    messages.info(request,'提交不合法')
                    return render(request, 'mywork/publish.html', locals())
        else:
            messages.info(request,'次数小于等于零,无法发表')
            return render(request, 'mywork/publish.html', locals())
    form = ArticleForm()
    return render(request,'mywork/publish.html',locals())

#--------------------积分----------------------------------

def score(request):
    user1 = request.session.get("username", False)
    bill_list = Bill.objects.all().order_by('-cost_date')
    if user1 != False:
        user1 = Users.objects.get(username=user1)
        paginator = Paginator(bill_list, 4)
        if request.method == 'POST':
            page = request.POST['tt']
        else:
            page = request.GET.get('page')
        try:
            customer = paginator.page(page)
        except PageNotAnInteger:
            customer = paginator.page(paginator.num_pages)
        except EmptyPage:
            customer = paginator.page(paginator.num_pages)
        bill_list = customer
        return render(request, 'mywork/score.html', locals())

#-------------------兑换 发布次数----------------------------
def duihuan(request):
    user1 = request.session.get("username", False)
    if user1 != False:
        user1 = Users.objects.get(username=user1)
        if request.method == 'POST':
            hidden = int(request.POST['hidden'])
            if user1.score >=2000:
                score = user1.score -hidden
                user1.score = score
                bill = Bill()
                bill.title = '兑换发表次数'
                bill.score = '-'+str(hidden)
                bill.author = user1
                bill.save()
                bill_list = Bill.objects.all()
                if hidden == 2000:
                    user1.leave_count +=5
                if hidden == 5000:
                    user1.leave_count +=10
                if hidden == 10000:
                    user1.leave_count +=20
                msg = '支付成功'
                user1.save()
                return HttpResponseRedirect(reverse('design:score',args=()))
            else:
                msg = "积分小于2000,不能支付"
        return render(request, 'mywork/duihuan.html', locals())


#---------------------我的发布------------------------------
def mypub(request,status):
    user1 = request.session.get("username", False)
    if user1 != False:
        user1 = Users.objects.get(username=user1)
        if status == 5:
            article_list = user1.authors.all()
        elif status == 1:
            article_list = user1.authors.filter(status=1)
        elif status == 2:
            article_list = user1.authors.filter(status=2)
        elif status == 0:
            article_list = user1.authors.filter(status=0)
        else:
            article_list = user1.authors.all()
        paginator = Paginator(article_list, 4)
        if request.method == 'POST':
            page = request.POST['tt']
        else:
            page = request.GET.get('page')
        try:
            customer = paginator.page(page)
        except PageNotAnInteger:
            customer = paginator.page(paginator.num_pages)
        except EmptyPage:
            customer = paginator.page(paginator.num_pages)
        article_list = customer
        return render(request, 'mywork/mypub.html', locals())

#--------------------消息----------------------------

def message(request):
    user1 = request.session.get("username")
    user1 = Users.objects.get(username=user1)
    comment_list = Comment.objects.filter(article__author=user1)
    paginator = Paginator(comment_list, 4)
    if request.method == 'POST':
        page = request.POST['tt']
    else:
        page = request.GET.get('page')
    try:
        customer = paginator.page(page)
    except PageNotAnInteger:
        customer = paginator.page(paginator.num_pages)
    except EmptyPage:
        customer = paginator.page(paginator.num_pages)
    comment_list = customer
    return render(request,'mywork/message.html',locals())

