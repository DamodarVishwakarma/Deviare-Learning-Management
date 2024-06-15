# Generated by Django 3.0.2 on 2020-11-02 02:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0032_auto_20201030_0900'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assessmentlicense',
            name='assessment_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assessment_licenses', to='main.Assessment'),
        ),
        migrations.AlterField(
            model_name='assessmentlicense',
            name='project_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assessment_licenses', to='main.Project'),
        ),
        migrations.AlterField(
            model_name='assessmentlicenseuser',
            name='assessment_license_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='users', to='main.AssessmentLicense'),
        ),
        migrations.AlterField(
            model_name='assessmentlicenseuser',
            name='user_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='registered_assessments', to='main.UserSettings'),
        ),
        migrations.AlterField(
            model_name='courselicense',
            name='course_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='course_licenses', to='main.Course'),
        ),
        migrations.AlterField(
            model_name='courselicense',
            name='project_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='course_licenses', to='main.Project'),
        ),
        migrations.AlterField(
            model_name='courselicenseuser',
            name='course_license_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='users', to='main.CourseLicense'),
        ),
        migrations.AlterField(
            model_name='courselicenseuser',
            name='user_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='registered_courses', to='main.UserSettings'),
        ),
    ]
