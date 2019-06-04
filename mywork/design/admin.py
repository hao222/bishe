from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
# Register your models here.
from design.models import AdminUser

admin.site.register(AdminUser, UserAdmin)