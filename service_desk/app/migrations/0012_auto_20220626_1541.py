# Generated by Django 3.2.13 on 2022-06-26 13:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0011_auto_20220626_1539'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auditlog',
            name='object',
            field=models.CharField(max_length=55, null=True),
        ),
        migrations.AlterField(
            model_name='auditlog',
            name='object_value',
            field=models.PositiveIntegerField(null=True),
        ),
    ]
