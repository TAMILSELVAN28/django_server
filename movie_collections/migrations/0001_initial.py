# Generated by Django 3.1 on 2020-11-17 16:08

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Users',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=200, null=True)),
                ('email_id', models.CharField(max_length=100, unique=True)),
                ('password', models.CharField(blank=True, max_length=200, null=True)),
                ('token', models.CharField(blank=True, max_length=500, null=True)),
            ],
        ),
    ]