# Generated by Django 4.0.4 on 2022-05-25 00:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0039_delete_statusassociation'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=55)),
                ('dest_status', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_dest_status', to='app.status')),
                ('src_status', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_src_status', to='app.status')),
            ],
            options={
                'verbose_name': 'transition',
                'verbose_name_plural': 'transitions',
                'db_table': 'transition',
                'ordering': ['src_status'],
            },
        ),
    ]