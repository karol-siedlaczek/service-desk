# Generated by Django 4.0.4 on 2022-05-25 00:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0034_tenant_customers_board_tenant_developers_board_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='board',
            old_name='type',
            new_name='env_type',
        ),
        migrations.RenameField(
            model_name='type',
            old_name='type',
            new_name='env_type',
        ),
    ]
