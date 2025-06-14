# Generated by Django 5.2.1 on 2025-06-01 21:52

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AdminTheme',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('css_url', models.CharField(blank=True, max_length=255, null=True)),
                ('js_url', models.CharField(blank=True, max_length=255, null=True)),
                ('is_active', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Admin Theme',
                'verbose_name_plural': 'Admin Themes',
            },
        ),
    ]
