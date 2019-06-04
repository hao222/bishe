#-*-coding:utf-8-*-
from .models import *
from django.forms import ModelForm,TextInput,Textarea,Select

class PeopleForm(ModelForm):
    class Meta:
        model = Users
        fields = ['nick_name','phone','photo','gender','info','address']
        widgets={
            'nick_name':TextInput(attrs={"class":"form-control","placeholder":"请输入昵称"}),
            'phone':TextInput(attrs={"class":"form-control","placeholder":"请输入手机号"}),
            'gender': Select(attrs={"class": "form-control", "placeholder": "性别:男,女"}),
            'info': TextInput(attrs={"class": "form-control", "placeholder": "个人简历"}),
            'address': Textarea(attrs={"class": "form-control", "placeholder": "地址"}),
        }


class ArticleForm(ModelForm):
    class Meta:
        model = Article
        fields = ['title','source','digest','image','ucontent','pubperson','category','author']
        widgets={
            'title':TextInput(attrs={'class':'form-control','placeholder':'请输入名称','id':'title'}),
            'source':TextInput(attrs={'class':'form-control','placeholder':'来源'}),
            'pubperson': TextInput(attrs={'class': 'form-control', 'placeholder': '原作者'}),
            'digest': TextInput(attrs={'class': 'form-control', 'placeholder': '摘要'}),
        }
