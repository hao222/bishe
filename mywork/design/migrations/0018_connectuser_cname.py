# Generated by Django 2.1.1 on 2018-12-18 15:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('design', '0017_share'),
    ]

    operations = [
        migrations.AddField(
            model_name='connectuser',
            name='cname',
            field=models.CharField(default='小吴', max_length=32),
        ),
    ]
