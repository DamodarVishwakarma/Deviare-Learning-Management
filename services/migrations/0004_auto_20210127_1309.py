# Generated by Django 3.0.2 on 2021-01-27 13:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0003_auto_20201110_1935'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='teampost',
            name='qualification',
        ),
        migrations.RemoveField(
            model_name='teampost',
            name='skills',
        ),
        migrations.DeleteModel(
            name='Qualification',
        ),
        migrations.DeleteModel(
            name='Skill',
        ),
        migrations.DeleteModel(
            name='TeamPost',
        ),
    ]
