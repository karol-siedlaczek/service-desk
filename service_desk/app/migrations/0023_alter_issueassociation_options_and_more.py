# Generated by Django 4.0.4 on 2022-05-23 15:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0022_remove_status_transition_name_status_transition'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='issueassociation',
            options={'verbose_name': 'link', 'verbose_name_plural': 'links'},
        ),
        migrations.RemoveField(
            model_name='issueassociation',
            name='type',
        ),
    ]