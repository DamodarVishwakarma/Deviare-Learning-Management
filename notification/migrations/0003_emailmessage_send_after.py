# Generated by Django 3.0.2 on 2021-04-20 20:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notification', '0002_auto_20210411_1700'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailmessage',
            name='send_after',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
