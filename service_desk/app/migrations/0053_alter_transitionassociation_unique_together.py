# Generated by Django 4.0.4 on 2022-05-25 01:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0052_alter_tenant_count'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='transitionassociation',
            unique_together={('issue_type', 'transition')},
        ),
    ]
