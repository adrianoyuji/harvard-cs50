# Generated by Django 3.2.8 on 2021-11-02 19:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0006_auto_20211024_1647'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='message',
            field=models.TextField(default='', max_length=256),
        ),
    ]
