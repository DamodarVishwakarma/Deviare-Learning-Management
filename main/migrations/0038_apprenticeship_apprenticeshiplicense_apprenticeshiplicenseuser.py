# Generated by Django 3.0.2 on 2021-04-06 19:03

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0037_auto_20210223_0559'),
    ]

    operations = [
        migrations.CreateModel(
            name='Apprenticeship',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('duration', models.CharField(max_length=30)),
                ('link', models.CharField(max_length=200)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ApprenticeshipLicense',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('count', models.IntegerField(default=1, null=True)),
                ('apprenticeship', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='apprenticeship_licenses', to='main.Apprenticeship')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='apprenticeship_licenses', to='main.Project')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ApprenticeshipLicenseUser',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('apprenticeship_license', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='users', to='main.ApprenticeshipLicense')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='registered_apprenticeships', to='main.UserSettings')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]