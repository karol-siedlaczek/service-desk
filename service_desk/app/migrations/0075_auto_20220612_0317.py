# Generated by Django 3.2.13 on 2022-06-12 01:17

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0074_auto_20220612_0316'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attachment',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to='F:\\Programs\\Repository\\Python\\Private\\GitHub\\service-desk_new_latest\\service_deskmedia/attachments', validators=[django.core.validators.FileExtensionValidator]),
        ),
        migrations.AlterField(
            model_name='issuetype',
            name='icon',
            field=models.ImageField(blank=True, max_length=500, upload_to='F:\\Programs\\Repository\\Python\\Private\\GitHub\\service-desk_new_latest\\service_deskmedia/img/issue_type', validators=[django.core.validators.FileExtensionValidator]),
        ),
        migrations.AlterField(
            model_name='priority',
            name='icon',
            field=models.ImageField(blank=True, max_length=500, upload_to='F:\\Programs\\Repository\\Python\\Private\\GitHub\\service-desk_new_latest\\service_deskmedia/img/priority', validators=[django.core.validators.FileExtensionValidator]),
        ),
        migrations.AlterField(
            model_name='tenant',
            name='icon',
            field=models.ImageField(blank=True, max_length=500, upload_to='F:\\Programs\\Repository\\Python\\Private\\GitHub\\service-desk_new_latest\\service_deskmedia/img/tenant', validators=[django.core.validators.FileExtensionValidator]),
        ),
    ]
