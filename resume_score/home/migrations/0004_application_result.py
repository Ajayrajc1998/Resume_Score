# Generated by Django 4.2.4 on 2023-09-09 06:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0003_uploadedfile_job'),
    ]

    operations = [
        migrations.CreateModel(
            name='Application_result',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(max_length=30)),
                ('title', models.CharField(max_length=100)),
                ('score_threshold', models.FloatField()),
            ],
        ),
    ]
