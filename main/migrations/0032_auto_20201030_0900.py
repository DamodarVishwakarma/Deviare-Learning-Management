# Generated by Django 3.0.2 on 2020-10-30 09:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0031_auto_20201019_0806'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='company_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='projects', to='main.Company'),
        ),
        migrations.AlterField(
            model_name='project',
            name='superadmin_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='project_created_by', to='main.UserSettings'),
        ),
    ]
