# Generated by Django 2.1.1 on 2018-11-27 20:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('design', '0007_users_add_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='users',
            name='add_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]