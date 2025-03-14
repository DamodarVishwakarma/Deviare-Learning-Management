# Generated by Django 3.0.2 on 2020-11-10 17:50

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TeamPost',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('position', models.CharField(max_length=250)),
                ('first_name', models.CharField(max_length=250, null=True)),
                ('surname', models.CharField(max_length=250, null=True)),
                ('short_desc', models.TextField(null=True)),
                ('experience', models.IntegerField(null=True)),
                ('skills', models.TextField(max_length=250, null=True)),
                ('qualification', models.TextField(max_length=250, null=True)),
                ('feature_picture', models.TextField(max_length=250, null=True)),
            ],
            options={
                'db_table': 'team_post',
            },
        ),
    ]
