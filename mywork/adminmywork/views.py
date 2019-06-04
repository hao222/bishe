import base64
import os

from django.contrib import messages
from django.contrib.auth import authenticate,logout,login as lg
from django.contrib.messages import get_messages
from django.core.files.base import ContentFile
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render,HttpResponseRedirect,reverse,HttpResponse
from django.views.decorators.csrf import csrf_exempt

from adminmywork.forms import CategoryForm, ArticleForm, AdminForm, UalterForm
from design.models import *
from mywork import settings
from .models import *
# Create your views here.
from adminmywork.tools import show_message


#----------------------------后台桌面-----------------
def desk(request):
    if not request.user.username:
        return HttpResponseRedirect(reverse('adminmywork:login'))
    return render(request, 'adminwork/desktop.html')


#----------------------登录页面----------------------
def login(request):
    if request.user.username:
        return HttpResponseRedirect(reverse('adminmywork:index'))
    return render(request, 'adminwork/login1.html', locals())

#--------------------验证登录-----------------------------
def login_check(request):
    if request.method == 'POST':
        username = request.POST.get('name')
        password = request.POST.get('password')
        user = authenticate(username=username,password=password)

        if user is not None:
            lg(request,user)
            systemlog = System_log()
            systemlog.user = AdminUser.objects.get(username=user)
            systemlog.username=user
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                systemlog.IP = x_forwarded_for.split(',')[-1].strip()
            else:
                systemlog.IP = request.META.get('REMOTE_ADDR')
            systemlog.save()
            return HttpResponse(show_message("success login!!",'/ff/manage/index/'))
        else:
            return HttpResponse(show_message("用户名或密码不正确",'/ff/manage/login/'))
    return HttpResponse(show_message("非法侵入",'/login/'))


#--------------------------退出登录----------------------
def log_out(request):
    logout(request)
    return render(request, 'adminwork/login1.html')

#---------------------------后台页面-------------------------
def index(request):
    if not request.user.username:
        return HttpResponseRedirect(reverse('adminmywork:index'))
    return render(request, 'adminwork/index.html')

#-------------------------类别管理admin_user-----------------
def sort(request):
    if not request.user.username:
        return HttpResponseRedirect(reverse('adminmywork:index'))
    else:
        search = request.POST.get("search")
        category_count = Sort.objects.all().count()
        if search is not None:
            if not search.isdigit():
                category_list = Sort.objects.filter(Sname__contains=search)
            else:
                category_list = Sort.objects.filter(Q(id=search) | Q(Sname__contains=search))
        else:
            category_list = Sort.objects.all()
    return render(request,'adminwork/sort_list.html',locals())


#分类添加:
def sort_add(request):
    storage = get_messages(request)
    if not request.user.username:
        return HttpResponseRedirect(reverse('adminmywork:index'))
    return render(request,'adminwork/sort_add.html',locals())

#分类保存
def sort_save(request):
    if not request.user.username:
        return HttpResponseRedirect(reverse('adminmywork:index'))
    else:
        if request.method== 'POST':
            c_name = request.POST.get('c_name')
            c_content = request.POST.get('c_content')
            if not c_name:
                messages.info(request,'分类名称不能为空')
                return HttpResponseRedirect(reverse('adminmywork:sort_add'))
            if not c_content:
                messages.info(request, '描述内容不能为空')
                return HttpResponseRedirect(reverse('adminmywork:sort_add'))
            if Sort.objects.filter(Sname=c_name).exists():
                messages.info(request,"名称已经存在!")
                return HttpResponseRedirect(reverse('adminmywork:sort_add'))
            category = Sort()
            category.Sname = c_name
            category.Scontent = c_content
            category.save()
            messages.info(request, "添加成功!")
            return HttpResponseRedirect(reverse('adminmywork:sort'))
    return render(request,'adminwork/sort_add.html',locals())

#修改类别
def sort_change(request):
    if not request.user.username:
        return HttpResponseRedirect(reverse('adminmywork:index'))
    c_id = request.GET.get('c_id')
    if c_id is None and not c_id.isdigit():
        return HttpResponseRedirect(reverse('adminmywork:sort'))
    try:
        category = Sort.objects.get(id=c_id)
    except Sort.DoesNotExist:
        return HttpResponseRedirect(reverse("adminmywork:sort"))
    form = CategoryForm(instance=category)
    return render(request, 'adminwork/sort_alter.html', locals())


def sort_save2(request):
    if not request.user.username:
        return HttpResponseRedirect(reverse('adminmywork:index'))
    if request.method =='POST':
        c_id = request.POST.get('c_id')
        category = Sort.objects.get(id=c_id)
        form = CategoryForm(request.POST,instance=category)
        if form.is_valid():
            form.save()
            messages.info(request,'修改成功!')
        else:
            messages.info(request,'修改失败!')
        return HttpResponseRedirect(reverse('adminmywork:sort'))


#删除类别
def sort_delete(request):
    if not request.user.username:
        return HttpResponseRedirect(reverse('adminmywork:index'))
    c_id = request.GET.get('c_id')
    if c_id is None:
        return JsonResponse({'status':0,'msg':'删除失败'})
    try:
        category = Sort.objects.get(id=c_id)
    except Sort.DoesNotExist:
        return JsonResponse({'status':2,'msg':'删除失败'})
    if category.categorys.all():
        return JsonResponse({'status': 2, 'msg': '删除失败'})
    category.delete()
    return JsonResponse({'status':1,'msg':'删除成功'})

#批量删除类别
def total_del(request):
    id_str = request.GET.get('cid')
    id_list = id_str.split(',')
    if not id_str:
        return JsonResponse({'status':2,'msg':"删除失败"})
    for id in id_list:
        if not id == "":
            category = Sort.objects.get(id=id)
            if category.categorys.all():
                return JsonResponse({'status': 2, 'msg': '删除失败'})
            category.delete()
            return JsonResponse({'status':1,'msg':"删除成功"})
#-------------------------分类  end-----------------------------------

#------------------发布策划以及策划的增删改查---------------------
def article_list(request):
    categories = Sort.objects.all()
    if not request.user.username:
        return HttpResponseRedirect(reverse('adminmywork:index'))
    if request.method == 'POST':
        search = request.POST.get("search")
        if search == 'true':
            c_id = int(request.POST.get('c_id'))
            start_date = request.POST.get("startdate")
            end_date = request.POST.get("enddate")
            title = request.POST.get("a_title")
            articles = get_data(c_id, start_date, end_date, title)
            return render(request, 'adminwork/article_list.html', locals())
        else:
            return HttpResponseRedirect(reverse('adminmywork:article_list'))
    else:
        articles = Article.objects.all()
        return render(request, 'adminwork/article_list.html', locals())


def get_data(c_id,start_date,end_date,title):
    if not c_id or not Sort.objects.filter(id=c_id).exists():
        articles = Article.objects.all()
    else:
        articles = Sort.objects.get(id=c_id).categorys.all()
    if start_date:
        articles = articles.filter(distribute_date__gte=start_date)
    if end_date:
        articles = articles.filter(distribute_date__lte=end_date)
    if title:
        # articles = articles.filter(title__contains=title)
        if not title.isdigit():
            articles = articles.filter(title__contains=title)
        else:
            articles = articles.filter(id=title)
    return articles


#添加策划
def article_add(request):
    if not request.user.username:
        return HttpResponseRedirect(reverse('adminmywork:login'))
    categories = Sort.objects.all()
    authors = Users.objects.all()
    return render(request,'adminwork/article_add.html',locals())


def article_save(request):
    if not request.user.username:
        return HttpResponseRedirect(reverse('adminmywork:index'))
    if request.method == 'POST':
        msg_dict = dict(title="标题", content="内容", digest="摘要", author="作者", source="来源", category_id='分类')
        article = Article()
        for k, v in request.POST.items():
            if not v and k != 'image':
                messages.info(request, msg_dict[k] + "不能为空")
                return HttpResponseRedirect(reverse('adminmywork:article_add'))
            article.__dict__[k] = v
        if 'image' in request.FILES:
            file = request.FILES['image']
            size = file.size
            if size >= 3 * 1024 * 1024:
                messages.info(request, "图片太大")
                return HttpResponseRedirect(reverse('adminmywork:article_add'))
            file2 = ContentFile(file.read())
            article.image.save(file.name, file2)
        article.save()
        messages.info(request, '添加成功')
        return HttpResponseRedirect(reverse('adminmywork:article_list'))
    else:
        return render(request, 'adminwork/article_add.html', locals())

#删除策划内容
def article_delete(request):
    a_id = request.GET.get('a_id')
    if a_id is None:
        return JsonResponse({'status':0,'msg':'删除文章失败'})
    else:
        try:
            article = Article.objects.get(id=a_id)
            path = settings.MEDIA_ROOT+str(article.image)
        except Article.DoesNotExist:
            return JsonResponse({'status':0,'msg':'删除失败'})
        if os.path.exists(path):
            os.remove(path)
        article.delete()
        return JsonResponse({'status':1,'msg':'删除成功'})

#批量删除策划
def all_del_article(request):
    id_str = request.GET.get("aid")
    id_list = id_str.split(",")
    if not id_str:
        return JsonResponse({'status': 2, 'msg': "删除失败"})
    for id in id_list:
        if not id == "":
            article = Article.objects.get(id=id)
            path = settings.MEDIA_ROOT + str(article.image)
            if os.path.exists(path):
                os.remove(path)
            article.delete()
            return JsonResponse({'status':1,'msg':"删除成功"})

#修改策划
def article_change(request):
    a_id = request.GET['a_id']
    if a_id is None and not a_id.isdigit():
        return HttpResponseRedirect(reverse('adminmywork:article_list'))
    try:
        article = Article.objects.get(id=a_id)
    except Article.DoesNotExist:
        return HttpResponseRedirect(reverse('adminmywork:article_list'))
    form = ArticleForm(instance=article)
    return render(request,'adminwork/article_change.html',locals())

def article_save2(request):
    if request.method == 'POST':
        a_id = request.POST.get("a_id")
        article = Article.objects.get(id=a_id)
        form = ArticleForm(request.POST,request.FILES, instance=article)
        path = settings.MEDIA_ROOT + str(article.image)
        if form.is_valid():
            if os.path.exists(path):
                os.remove(path)
            form.save()
            messages.info(request,'修改成功')
        else:
            messages.info(request, '修改失败')
        return HttpResponseRedirect(reverse('adminmywork:article_list'))


#审核策划
def article_shenhe1(request):
    a_id = request.GET.get('a_id')
    if a_id is None:
        return JsonResponse({'status': 3, 'msg': '匹配不到'})
    else:
        try:
            article = Article.objects.get(id=a_id)
        except Article.DoesNotExist:
            return JsonResponse({'status':3,'msg':'匹配不到'})
        status = article.status
        if status == 0:
            return JsonResponse({'status':0,'msg':'未审核'})
        if status == 1:
            return JsonResponse({'status':1,'msg':'通过'})
        if status == 2:
            return JsonResponse({'status':2,'msg':'未通过'})

    return HttpResponse("非法进入")

def article_check(request):
    a_id = request.GET.get('a_id')
    article = Article.objects.get(id=a_id)
    if 'status' in request.GET:
        status = int(request.GET['status'])
        article.status = status
        article.save()
        if status == 0:
            return JsonResponse({'status': 0, 'msg': '未审核'})
        if status == 1:
            return JsonResponse({'status': 1, 'msg': '通过'})
        if status == 2:
            return JsonResponse({'status': 2, 'msg': '未通过'})

    return HttpResponse("非法进入")
#--------------------------------策划end------------------------------


#------------------------------个人信息-------------------------------
def info_admin(request):
    if not request.user.username:
        return HttpResponseRedirect(reverse('adminmywork:index'))
    else:
        user1 = request.user
        print(user1,'-----')
        # form = AForm(instance=user1)
        # print(form,'==================')
    return render(request,'adminwork/info_admin.html',locals())
#---------------------------------- end----------------------------------


#-------------------------------管理员管理------------------------------

#角色展示
def admin_list(request):
    if not request.user.username:
        return HttpResponseRedirect(reverse('adminmywork:index'))
    else:
        admins = AdminUser.objects.all()
        admins_count = AdminUser.objects.count()
    return render(request,'adminwork/admin_list.html',locals())

#角色添加
def admin_add(request):
    form = AdminForm()
    return render(request,'adminwork/admin-add.html',locals())

def admin_save(request):
    if request.method == 'POST':
        form =AdminForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            phone = form.cleaned_data['phone']
            email = form.cleaned_data['email']
            admin_rool = form.cleaned_data['admin_rool']
            gender = form.cleaned_data['gender']
            rool_info = form.cleaned_data['rool_info']
            admin = AdminUser.objects.create_user(username=username,password=password,phone=phone,email=email,admin_rool=admin_rool,gender=gender,rool_info=rool_info)
            return JsonResponse({'status':1,'msg':'添加成功'})
    return render(request,'adminwork/admin_list.html',locals())

#用户名检测
def user_check(request):
    if request.method == 'GET':
        username = request.GET.get('username',False)
        if AdminUser.objects.filter(username=username).exists():
            return JsonResponse({'status':0,"msg":'用户存在'})
        else:
            return JsonResponse({'status':1,'msg':'可以使用'})
    else:
        return JsonResponse({'status':2,"msg":'非法'})

#手机号检测
def phone_check(request):
    if request.method == 'GET':
        phone = request.GET.get('phone',False)
        if AdminUser.objects.filter(phone=phone).exists():
            return JsonResponse({'status':0,"msg":'手机号已存在'})
        else:
            return JsonResponse({'status':1,'msg':'可以使用'})
    else:
        return JsonResponse({'status':2,"msg":'非法'})

#角色更改
def admin_change(request):
    a_id = request.GET['a_id']
    if a_id is None and not a_id.isdigit():
        return HttpResponseRedirect(reverse('adminmywork:admin_list'))
    try:
        admin = AdminUser.objects.get(id=a_id)

    except AdminUser.DoesNotExist:
        return HttpResponseRedirect(reverse('adminmywork:article_list'))
    form = UalterForm(instance=admin)
    return render(request,'adminwork/admin_change.html',locals())

def admin_save2(request):
    if request.method == 'POST':
        a_id = request.POST.get('a_id')
        admin = AdminUser.objects.get(id=a_id)
        form = UalterForm(request.POST,instance=admin)
        if form.is_valid():
            a = form.save()
            a.set_password(a.password)
            a.save()
    return render(request, 'adminwork/admin_list.html', locals())

#角色删除
def admin_del(request):
    a_id = request.GET.get('a_id')
    if a_id is None:
        return JsonResponse({'status': 0, 'msg': '删除用户失败'})
    else:
        try:
            admin = AdminUser.objects.get(id=a_id)
        except Article.DoesNotExist:
            return JsonResponse({'status': 0, 'msg': '删除失败'})
        admin.delete()
        return JsonResponse({'status': 1, 'msg': '删除成功'})

#角色批量删除
def admin_alldel(request):
    id_str = request.GET.get("a_id")
    id_list = id_str.split(",")
    if not id_str:
        return JsonResponse({'status': 2, 'msg': "删除失败"})
    for id in id_list:
        if not id == "":
            try:
                admin = AdminUser.objects.get(id=id)
            except Article.DoesNotExist:
                return JsonResponse({'status': 0, 'msg': '删除失败'})
            admin.delete()
            return JsonResponse({'status': 1, 'msg': "删除成功"})

#--------------------------end---------------------------


#--------------------留言 联系我们 -----------------------
def connect(request):
    connects = ConnectUser.objects.all()
    connect_count = ConnectUser.objects.count()
    if request.method == 'POST':
        search = request.POST.get('search')
        if search == 'true':
            start_date = request.POST.get('startdate')
            end_date = request.POST.get('enddate')
            name = request.POST.get('name')
            if start_date:
                connects = connects.filter(pu_date__gte=start_date)
            if end_date:
                connects = connects.filter(pu_date__lte=end_date)
            if name is not None:
                if not name.isdigit():
                    connects = connects.filter(name__username__contains=name)
                else:
                    connects = connects.filter(Q(id=name) | Q(name__username__contains=name))
    return render(request,'adminwork/feedback-list.html',locals())


#删除留言
def connect_del(request):
    cid = request.GET.get('cid')
    if cid is None:
        return JsonResponse({'status':0,'msg':'删除失败'})
    else:
        try:
            connect = ConnectUser.objects.get(id=cid)
        except ConnectUser.DoesNotExist:
            return JsonResponse({'status':0,'msg':'删除失败'})
        connect.delete()
        return JsonResponse({'status': 1, 'msg': '删除成功'})

#批量删除
def connect_alldel(request):
    id_str = request.GET.get("cid")
    id_list = id_str.split(",")
    if not id_str:
        return JsonResponse({'status': 2, 'msg': "删除失败"})
    for id in id_list:
        if not id == "":
            try:
                connect = ConnectUser.objects.get(id=id)
            except ConnectUser.DoesNotExist:
                return JsonResponse({'status': 0, 'msg': '删除失败'})
            connect.delete()
            return JsonResponse({'status': 1, 'msg': "删除成功"})

#---------------------------end------------------------------------

#---------------------留言用户信息查看-----------------------------
def connect_show(request):
    cid = request.GET.get('cid')
    connect = ConnectUser.objects.get(id=cid)
    return render(request,'adminwork/connectuser_show.html',locals())


def aa(request):
    return render(request,'adminwork/prodect.html')

#---------------------系统日志-------------------------------------
def system_log(request):
    if not request.user.username:
        return HttpResponseRedirect(reverse('adminmywork:index'))
    else:
        systemlogs = System_log.objects.all()
        if request.method == 'POST':
            search = request.POST.get('search')
            if search == 'true':
                title = request.POST.get('title')
                if title:
                    if not title.isdigit():
                        systemlogs = systemlogs.filter(content__contains=title)
                    else:
                        systemlogs = systemlogs.filter(id=title)
    return render(request,'adminwork/system-log.html',locals())

#----------------------删除日志--------------------------------
@csrf_exempt
def systemlog_delete(request):
    sid = request.GET.get('s_id')
    if sid is None:
        return JsonResponse({'status': 0, 'msg': '删除失败'})
    else:
        try:
            connect = System_log.objects.get(id=sid)
        except ConnectUser.DoesNotExist:
            return JsonResponse({'status': 0, 'msg': '删除失败'})
        connect.delete()
        return JsonResponse({'status': 1, 'msg': '删除成功'})

#---------------------批量删除log--------------------------------
def system_log_alldel(request):
    ids = request.GET.get("sid")
    id_list = ids.split(",")
    if not ids:
        return JsonResponse({'status': 2, 'msg': "删除失败"})
    for id in id_list:
        if not id == "":
            try:
                systemlog = System_log.objects.get(id=id)
            except System_log.DoesNotExist:
                return JsonResponse({'status': 0, 'msg': '删除失败'})
            systemlog.delete()
            return JsonResponse({'status': 1, 'msg': "删除成功"})
