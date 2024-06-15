# Generated by Django 3.0.2 on 2021-09-14 11:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0044_project_is_delete'),
    ]

    operations = [
        migrations.CreateModel(
            name='ElearninStates',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(blank=True, max_length=120, null=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
            ],
        ),
    ]