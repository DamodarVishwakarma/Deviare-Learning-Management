# Generated by Django 3.0.6 on 2020-06-23 11:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("main", "0014_auto_20200622_1610")]

    operations = [
        migrations.AlterField(
            model_name="course", name="description", field=models.TextField(blank=True)
        )
    ]
