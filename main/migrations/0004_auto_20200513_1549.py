# Generated by Django 3.0.6 on 2020-05-13 10:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("main", "0003_usersettings")]

    operations = [
        migrations.DeleteModel(name="User"),
        migrations.DeleteModel(name="UserSettings"),
    ]
