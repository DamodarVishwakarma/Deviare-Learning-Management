# Generated by Django 3.0.2 on 2021-01-27 13:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('main', '0034_merge_20201103_1230'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, default='', max_length=255)),
                ('image', models.TextField(default='https://api-staging.deviare.co.za/static/images/default.png')),
                ('cat_id', models.IntegerField(default=0)),
            ],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='CourseProduct',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, default='', max_length=255)),
                ('product_id', models.IntegerField(default=0)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='courses', to='wp_api.Category')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wc_product', to='main.Course')),
            ],
            options={
                'verbose_name': 'Course Product',
                'verbose_name_plural': 'Course Products',
            },
        ),
    ]
