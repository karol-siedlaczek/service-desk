# Generated by Django 4.0.4 on 2022-06-01 22:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0053_alter_transitionassociation_unique_together'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='status',
            options={'ordering': ['name'], 'verbose_name': 'status', 'verbose_name_plural': 'statuses'},
        ),
        migrations.AlterModelOptions(
            name='tenant',
            options={'ordering': ['id'], 'permissions': [('view_customer_space', "User can manage and view tenant's issues with customer level permission"), ('view_operator_space', "User can manage and view tenant's issues with operator level permission"), ('view_developer_space', "User can manage and view tenant's issues with developer level permission")], 'verbose_name': 'tenant', 'verbose_name_plural': 'tenants'},
        ),
    ]