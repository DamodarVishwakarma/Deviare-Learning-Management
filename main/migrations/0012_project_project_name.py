# Generated by Django 3.0.6 on 2020-06-17 09:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("main", "0011_auto_20200616_1719")]

    operations = [
        migrations.AddField(
            model_name="project",
            name="project_name",
            field=models.CharField(blank=True, max_length=100, null=True),
        )
    ]
