# Generated by Django 3.0.6 on 2020-06-17 19:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [("main", "0012_project_project_name")]

    operations = [
        migrations.AlterField(
            model_name="courselicenseuser",
            name="user_id",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="main.UserSettings"
            ),
        )
    ]
