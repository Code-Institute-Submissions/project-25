# Generated by Django 3.1.3 on 2020-12-08 13:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_auto_20201201_1505'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='rating',
            field=models.IntegerField(blank=True, default=False, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='size_lg',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='size_m',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='size_s',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='size_xl',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]
