# Generated by Django 2.1.1 on 2018-11-27 19:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('design', '0004_connectuser'),
    ]

    operations = [
        migrations.AlterField(
            model_name='connectuser',
            name='pu_date',
            field=models.DateField(auto_now_add=True),
        ),
    ]