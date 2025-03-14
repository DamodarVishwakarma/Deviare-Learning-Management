# Generated by Django 3.0.6 on 2020-06-25 05:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("main", "0015_auto_20200623_1656")]

    operations = [
        migrations.AddField(
            model_name="course",
            name="course_type",
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AlterUniqueTogether(
            name="course", unique_together={("course_id", "course_type")}
        ),
    ]
