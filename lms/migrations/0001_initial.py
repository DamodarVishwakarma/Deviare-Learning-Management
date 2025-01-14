# Generated by Django 3.0.2 on 2021-02-15 04:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('main', '0035_auto_20210215_0412'),
    ]

    operations = [
        migrations.CreateModel(
            name='TimelineAction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, default='', max_length=100, unique=True)),
                ('verbose_name', models.CharField(default='', max_length=100)),
            ],
            options={
                'verbose_name': 'Timeline Action',
                'verbose_name_plural': 'Timeline Actions',
            },
        ),
        migrations.CreateModel(
            name='Timeline',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField(default='')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('object', models.CharField(default='-', max_length=10)),
                ('object_name', models.CharField(default='-', max_length=150)),
                ('secondary_object', models.CharField(default='-', max_length=10)),
                ('secondary_object_name', models.CharField(default='-', max_length=150)),
                ('event_counter', models.CharField(default='1', max_length=10)),
                ('action', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='events', to='lms.TimelineAction')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='lms_events', to='main.UserSettings')),
            ],
            options={
                'verbose_name': 'Timeline',
                'verbose_name_plural': 'Timelines',
            },
        ),
    ]
