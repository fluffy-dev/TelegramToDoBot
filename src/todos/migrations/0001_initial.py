# Generated by Django 5.2.3 on 2025-06-26 15:47

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('created_at', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.CharField(editable=False, max_length=64, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='categories', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
                'unique_together': {('user', 'name')},
            },
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('created_at', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.CharField(editable=False, max_length=64, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('due_date', models.DateTimeField()),
                ('is_completed', models.BooleanField(default=False)),
                ('notification_sent', models.BooleanField(default=False)),
                ('categories', models.ManyToManyField(blank=True, related_name='tasks', to='todos.category')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Task',
                'verbose_name_plural': 'Tasks',
                'ordering': ('-created_at',),
            },
        ),
    ]
