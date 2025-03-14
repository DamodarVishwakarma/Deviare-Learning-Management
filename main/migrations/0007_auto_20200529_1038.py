# Generated by Django 3.0.6 on 2020-05-29 05:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("main", "0006_usersettings_validated"),
    ]

    operations = [
        migrations.CreateModel(
            name="Assessment",
            fields=[
                (
                    "_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField()),
                ("duration", models.CharField(max_length=30)),
                ("link", models.CharField(max_length=200)),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="Company",
            fields=[
                (
                    "_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=100)),
                ("country", models.CharField(max_length=20)),
                ("address", models.CharField(max_length=100)),
                ("email", models.EmailField(max_length=150, unique=True)),
                ("contact_no", models.BigIntegerField()),
                ("logo", models.URLField(null=True)),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="Course",
            fields=[
                (
                    "_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField()),
                ("provider", models.CharField(max_length=30)),
                ("link", models.CharField(max_length=200)),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="CourseLicense",
            fields=[
                (
                    "_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("count", models.IntegerField()),
                (
                    "course",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="main.Course"
                    ),
                ),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="Deployment",
            fields=[
                (
                    "_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField()),
                ("repository", models.CharField(max_length=200)),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="Experiment",
            fields=[
                (
                    "_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField()),
                ("link", models.CharField(max_length=200)),
            ],
            options={"abstract": False},
        ),
        migrations.AddField(
            model_name="usersettings",
            name="contact_no",
            field=models.BigIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="usersettings",
            name="country",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="usersettings",
            name="email",
            field=models.EmailField(blank=True, max_length=150, null=True, unique=True),
        ),
        migrations.AddField(
            model_name="usersettings",
            name="firstName",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="usersettings",
            name="is_active",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="usersettings",
            name="is_staff",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="usersettings",
            name="is_superuser",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="usersettings",
            name="lastName",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="usersettings",
            name="location",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="usersettings",
            name="password",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="usersettings",
            name="profile_image",
            field=models.URLField(null=True),
        ),
        migrations.AddField(
            model_name="usersettings",
            name="userName",
            field=models.CharField(blank=True, max_length=100, null=True, unique=True),
        ),
        migrations.CreateModel(
            name="Project",
            fields=[
                (
                    "_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("status", models.CharField(max_length=20)),
                (
                    "admin",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="main.UserSettings",
                    ),
                ),
                (
                    "company",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="main.Company"
                    ),
                ),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="CourseUser",
            fields=[
                (
                    "_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "user_license",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="main.CourseLicense",
                    ),
                ),
            ],
            options={"abstract": False},
        ),
        migrations.AddField(
            model_name="courselicense",
            name="project",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="main.Project"
            ),
        ),
        migrations.AddField(
            model_name="usersettings",
            name="companyID",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="main.Company",
            ),
        ),
    ]
