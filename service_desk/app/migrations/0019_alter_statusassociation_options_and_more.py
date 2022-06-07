# Generated by Django 4.0.4 on 2022-05-23 15:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0018_remove_status_status_type_alter_type_type'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='statusassociation',
            options={'ordering': ['status'], 'verbose_name': 'status association', 'verbose_name_plural': 'status associations'},
        ),
        migrations.AddField(
            model_name='statusassociation',
            name='resolution',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_issue_type', to='app.resolution'),
        ),
    ]