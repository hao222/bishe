# Generated by Django 2.1.1 on 2019-04-21 00:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('design', '0022_auto_20190420_2350'),
    ]

    operations = [
        migrations.AlterField(
            model_name='users',
            name='photo',
            field=models.ImageField(default='tou.jpg', upload_to='media/'),
        ),
    ]
