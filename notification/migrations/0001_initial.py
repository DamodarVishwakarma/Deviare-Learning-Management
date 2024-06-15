# Generated by Django 3.0.2 on 2021-02-17 02:41

from django.db import migrations, models
import django.db.models.deletion
import django_mysql.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EmailTemplate',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=250)),
                ('body_text', models.TextField(blank=True, default='')),
                ('body_html', models.TextField(blank=True, default='')),
            ],
            options={
                'db_table': 'email_template',
            },
        ),
        migrations.CreateModel(
            name='EmailMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipient', models.CharField(max_length=50, verbose_name='Recipient Email')),
                ('subject', models.CharField(max_length=255, verbose_name='Subject')),
                ('content', django_mysql.models.JSONField(default=dict)),
                ('sent', models.BooleanField(default=False)),
                ('sent_at', models.DateTimeField(null=True)),
                ('template', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='notification.EmailTemplate')),
            ],
            options={
                'verbose_name': 'EmailMessage',
                'verbose_name_plural': 'EmailMessages',
            },
        ),
    ]
