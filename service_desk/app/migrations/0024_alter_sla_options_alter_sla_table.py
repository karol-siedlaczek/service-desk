# Generated by Django 4.0.4 on 2022-05-23 21:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0023_alter_issueassociation_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='sla',
            options={'ordering': ['id'], 'verbose_name': 'SLA scheme', 'verbose_name_plural': 'SLA schemes'},
        ),
        migrations.AlterModelTable(
            name='sla',
            table='SLA',
        ),
    ]