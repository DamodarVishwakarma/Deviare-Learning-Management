# Generated by Django 3.0.2 on 2020-10-07 01:13

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0027_updaterecords'),
    ]

    operations = [
        migrations.CreateModel(
            name='TMForumCriterion',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('value', models.IntegerField(null=True)),
                ('title', models.CharField(blank=True, max_length=255, null=True)),
                ('description', models.TextField(blank=True, max_length=255, null=True)),
            ],
            options={
                'db_table': 'tmforum_criterion',
            },
        ),
        migrations.CreateModel(
            name='TMForumDimension',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(blank=True, max_length=255, null=True)),
                ('value', models.IntegerField(null=True)),
            ],
            options={
                'db_table': 'tmforum_dimension',
            },
        ),
        migrations.CreateModel(
            name='TMForumRatingDetail',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('value', models.IntegerField(null=True)),
                ('title', models.CharField(blank=True, max_length=255, null=True)),
                ('description', models.TextField(blank=True, max_length=255, null=True)),
                ('criterion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rating_details', to='main.TMForumCriterion')),
            ],
            options={
                'db_table': 'tmforum_rating_detail',
            },
        ),
        migrations.CreateModel(
            name='TMForumUserResponse',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('comment', models.TextField(blank=True, null=True)),
                ('document', models.TextField(blank=True, null=True)),
                ('aspiration', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user_aspiration', to='main.TMForumRatingDetail')),
                ('criterion', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user_responses', to='main.TMForumCriterion')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tmforum_assessment_responses', to='main.UserSettings')),
                ('status_quo', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user_status_quo', to='main.TMForumRatingDetail')),
            ],
            options={
                'db_table': 'tmforum_user_response',
            },
        ),
        migrations.CreateModel(
            name='TMForumUserAssessment',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('criterion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_assessment', to='main.TMForumCriterion')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tmforum_assessment_criteria', to='main.UserSettings')),
            ],
            options={
                'db_table': 'tmforum_user_assessement',
            },
        ),
        migrations.CreateModel(
            name='TMForumSubDimension',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('value', models.IntegerField(null=True)),
                ('title', models.CharField(blank=True, max_length=255, null=True)),
                ('description', models.TextField(blank=True, max_length=255, null=True)),
                ('dimension', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subDimensions', to='main.TMForumDimension')),
            ],
            options={
                'db_table': 'tmforum_sub_dimension',
            },
        ),
        migrations.AddField(
            model_name='tmforumcriterion',
            name='sub_dimension',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='criteria', to='main.TMForumSubDimension'),
        ),
        migrations.CreateModel(
            name='TMForumAssignedAssessment',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('assessment', models.ManyToManyField(null=True, related_name='assigned', to='main.TMForumUserAssessment')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tmforum_assessment', to='main.Company')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tmforum_assessment', to='main.UserSettings')),
            ],
            options={
                'db_table': 'tmforum_assigned_assessement',
            },
        ),
    ]