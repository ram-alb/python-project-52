# Generated by Django 4.2 on 2024-02-09 03:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0004_alter_tasks_author_alter_tasks_executor'),
        ('labels', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Labels',
            new_name='Label',
        ),
    ]