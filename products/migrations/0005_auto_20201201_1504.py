# Generated by Django 3.1.3 on 2020-12-01 15:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_auto_20201201_1500'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='size_lg',
            new_name='size_xl',
        ),
    ]
