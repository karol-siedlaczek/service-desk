# Generated by Django 3.2.9 on 2022-06-16 17:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_auto_20220616_1905'),
    ]

    operations = [
        migrations.AlterField(
            model_name='priority',
            name='step',
            field=models.IntegerField(default=1),
        ),
    ]
