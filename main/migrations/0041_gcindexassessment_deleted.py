# Generated by Django 3.0.2 on 2021-04-22 01:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0040_gcindexassessmenttrack'),
    ]

    operations = [
        migrations.AddField(
            model_name='gcindexassessment',
            name='deleted',
            field=models.BooleanField(default=False, null=True),
        ),
    ]
