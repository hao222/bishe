# Generated by Django 2.1.1 on 2018-11-27 20:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('design', '0006_users_gender'),
    ]

    operations = [
        migrations.AddField(
            model_name='users',
            name='add_date',
            field=models.DateTimeField(default='2018-11-23 04:44:28.080586'),
        ),
    ]
