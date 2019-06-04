#-*-coding:utf-8-*-
from django import forms
from .models import *
from design.models import *


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Sort
        fields = ['Sname','Scontent']
        widgets = {
            'Sname':forms.TextInput(attrs={"class":'input-text','name':'c_name','id':'c_name'}),
            'Scontent':forms.TextInput(attrs={"class":"textarea",'name':'c_content','id':'c_content','onkeyup':'$(this).Huitextarealength(this,200)'})
        }

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title','digest','source','content','author','image','category']
        widgets = {
            'title':forms.TextInput(attrs={"class":'input-text','name':'title','id':'articletitle'}),
            'content':forms.Textarea(attrs={'id':'editor','name':'content'}),
            'digest':forms.Textarea(attrs={'class':'textarea','name':'digest','onkeyup':'$(this).Huitextarealength(this,140)'}),
            'author':forms.TextInput(attrs={"class":'input-text','name':'author','id':'author'}),
            'source': forms.TextInput(attrs={"class": 'input-text', 'name': 'source', 'id': 'sources'}),

            'category':forms.Select(attrs={'name':'articletype','class':'select'}),
        }

choices_admin = (
    (0, '超级管理员'),
    (1, '类别总编'),
    (2, '策划总编'),
    (3,'管理员监查员')
)

class AdminForm(forms.Form):
    username = forms.CharField(max_length=32,widget=forms.TextInput(attrs={'class':'input-text username','name':'username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'input-text','name':'password'}))
    gender = forms.CharField(max_length=2,widget=forms.TextInput(attrs={'class':'input-text','name':'gender'}))
    phone = forms.CharField(max_length=11,widget=forms.TextInput(attrs={'class':'input-text phone'}))
    email = forms.EmailField(max_length=12,widget=forms.EmailInput(attrs={'class':'input-text','name':'email'}))
    admin_rool = forms.ChoiceField(widget=forms.Select(attrs={'class':'input-text'}),choices=choices_admin,initial=2)
    rool_info = forms.CharField(max_length=100,widget=forms.Textarea(attrs={'class':'textarea','name':'beizhu','onkeyup':'$(this).Huitextarealength(this,140)'}))

class UalterForm(forms.ModelForm):
    class Meta:
        model = AdminUser
        fields = ['username','password','gender','phone','email','admin_rool','rool_info']
        widgets = {
            'password':forms.PasswordInput(attrs={'class':'input-text'}),
            'username': forms.TextInput(attrs={'class': 'input-text username', 'id': 'username', 'name': 'username'}),
            'phone': forms.TextInput(attrs={'class': 'input-text phone'}),
            'email': forms.EmailInput(attrs={'class': 'input-text', 'id': 'email', 'name': 'email'}),
            'rool_info': forms.Textarea(
                attrs={'class': 'textarea', 'name': 'beizhu', 'onkeyup': '$(this).Huitextarealength(this,140)'}),
            'gender': forms.TextInput(attrs={'class': 'input-text'}),
            'admin_rool':forms.Select(choices=choices_admin,attrs={'class': 'input-text'})
        }
