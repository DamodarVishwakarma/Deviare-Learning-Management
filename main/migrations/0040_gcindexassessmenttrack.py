# Generated by Django 3.0.2 on 2021-04-20 20:19

from django.db import migrations, models
import django.db.models.deletion
import main.fields


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0039_auto_20210411_1700'),
    ]

    operations = [
        migrations.CreateModel(
            name='GCIndexAssessmentTrack',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('updated_fields', main.fields.SimpleJSONField(default=list, null=True)),
                ('assessment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='track', to='main.GCIndexAssessment')),
                ('state', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='track', to='main.GCState')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]