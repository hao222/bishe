# Generated by Django 2.1.1 on 2018-11-27 20:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('design', '0005_auto_20181127_1907'),
    ]

    operations = [
        migrations.AddField(
            model_name='users',
            name='gender',
            field=models.SmallIntegerField(choices=[(0, '男'), (1, '女'), (2, '未知')], default=0),
        ),
    ]