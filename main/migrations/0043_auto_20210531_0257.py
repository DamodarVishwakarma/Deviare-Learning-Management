# Generated by Django 3.0.2 on 2021-05-31 02:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0042_auto_20210531_0241'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apprenticeship',
            name='link',
            field=models.TextField(null=True),
        ),
    ]
