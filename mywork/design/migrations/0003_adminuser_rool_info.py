# Generated by Django 2.1.1 on 2018-11-26 08:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('design', '0002_adminuser_admin_rool'),
    ]

    operations = [
        migrations.AddField(
            model_name='adminuser',
            name='rool_info',
            field=models.CharField(default='1', max_length=200),
        ),
    ]
