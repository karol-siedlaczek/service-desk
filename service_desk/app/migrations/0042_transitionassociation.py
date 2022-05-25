# Generated by Django 4.0.4 on 2022-05-25 00:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0041_status_transitions'),
    ]

    operations = [
        migrations.CreateModel(
            name='TransitionAssociation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('issue_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_issue_type', to='app.issuetype')),
                ('transition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_transition', to='app.transition')),
            ],
            options={
                'verbose_name': 'transition association',
                'verbose_name_plural': 'transition associations',
                'db_table': 'transition_association',
                'ordering': ['transition'],
            },
        ),
    ]
