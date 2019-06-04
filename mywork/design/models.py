from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from DjangoUeditor.models import UEditorField
# Create your models here.

class Users(models.Model):
    username = models.CharField(max_length=20,unique=True)
    password = models.CharField(max_length=32)
    photo = models.ImageField(upload_to="",default='tou.jpg')
    phone = models.CharField(max_length=11,unique=True)
    money = models.PositiveIntegerField(default=0)
    info = models.CharField(max_length=200,default="多多益善")
    leave_count = models.PositiveSmallIntegerField(default=0)
    nick_name = models.CharField(max_length=20,default="翱翔")
    email = models.EmailField()
    blank = models.CharField(max_length=32,default=0)
    choices_sex = (
        (0,'男'),
        (1,'女'),
        (2,'未知')
    )
    gender = models.SmallIntegerField(choices=choices_sex,default=0)
    add_date = models.DateTimeField(auto_now_add=True)
    score = models.IntegerField(default=0)
    address = models.CharField(max_length=64,default='北京市 雄安区')
    def __str__(self):
        return self.username


class Sort(models.Model):
    Sname = models.CharField(max_length=64,unique=True)
    Scontent = models.TextField(max_length=200)

    class Meta:
        db_table='admin_sort'
        ordering=['Sname']

    def __str__(self):
        return self.Sname


class AdminUser(AbstractUser):
    phone = models.CharField(max_length=11,unique=True)
    gender = models.CharField(max_length=2,default='男')
    admin_info = models.CharField(max_length=200,default='一个无聊的人')
    choices_admin = (
        (0, '超级管理员'),
        (1, '类别总编'),
        (2, '策划总编'),
        (3,'管理员监查员')
    )
    admin_rool = models.PositiveIntegerField(choices=choices_admin, default=0)
    rool_info = models.CharField(max_length=200,default='1')
    def __str__(self):
        return self.username


class Article(models.Model):
    author = models.ForeignKey(Users,on_delete=models.CASCADE,related_name='authors')
    category = models.ForeignKey(Sort,on_delete=models.PROTECT,related_name='categorys')
    title = models.CharField(max_length=50)
    source = models.CharField(max_length=50,null=True)
    digest = models.CharField(max_length=100)
    image = models.ImageField(upload_to='active/%Y%m%d/')
    content = models.TextField(default=0)
    pubperson = models.CharField(max_length=64,default='----')
    view_count = models.PositiveIntegerField(default=0)
    share_count = models.PositiveIntegerField(default=0)
    distribute_date = models.DateTimeField(auto_now_add=True)
    votes_count = models.PositiveIntegerField(default=0)
    status_choice=(
        (0,'未审核'),
        (1,'审核通过'),
        (2,'审核未通过')
    )
    status = models.PositiveIntegerField(choices=status_choice,default=0)
    ucontent = UEditorField('富文本新闻内容', width=600, height=300, toolbars='full',
                           imagePath='', filePath='',
                           upload_settings={"imageMaxSize": 1204000},
                           settings={}, command=None,
                           blank=True)

    def increase_views(self):
        self.view_count +=1
        self.save(update_fields=['view_count'])

    def get_absolute_url(self):
        return reverse('design:detail',kwargs={'aid':self.id})

    def __str__(self):
        return self.title


class ConnectUser(models.Model):
    cname = models.CharField(max_length=32,default='0')
    name = models.ForeignKey(Users,on_delete=models.CASCADE,related_name='connects')
    phone = models.CharField(max_length=11)
    QQ = models.CharField(max_length=12)
    email = models.EmailField()
    message = models.TextField()
    pu_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name.username

class Bill(models.Model):
    author = models.ForeignKey(Users,on_delete=models.CASCADE,related_name='bills')
    title = models.CharField(max_length=20,default="积分账单")
    score = models.CharField(max_length=10,default="+50")
    cost_date = models.DateTimeField(auto_now_add=True)


class Comment(models.Model):
    user = models.ForeignKey(Users,on_delete=models.CASCADE,default=0)
    article = models.ForeignKey(Article,related_name='comments',on_delete=models.DO_NOTHING)
    content = models.CharField(max_length=100)
    send_time = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    user = models.ForeignKey(Users,on_delete=models.CASCADE,default=0)
    article = models.ForeignKey(Article,related_name='message',on_delete=models.DO_NOTHING)
    content = models.CharField(max_length=100)
    pub_time = models.DateTimeField(auto_now_add=True)



class Likes(models.Model):
    author = models.ForeignKey(Users, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)

class Share(models.Model):
    author = models.ForeignKey(Users, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)


class System_log(models.Model):
    user = models.ForeignKey(AdminUser,on_delete=models.CASCADE)
    content = models.CharField(max_length=32,default='登录成功!')
    username = models.CharField(max_length=32,default=user)
    pu_date = models.DateTimeField(auto_now_add=True)
    IP = models.CharField(max_length=64,default='127.0.0.1')
