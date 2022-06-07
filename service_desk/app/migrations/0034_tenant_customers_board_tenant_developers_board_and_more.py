# Generated by Django 4.0.4 on 2022-05-23 23:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0033_alter_board_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='tenant',
            name='customers_board',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='%(class)s_customers_board', to='app.board'),
        ),
        migrations.AddField(
            model_name='tenant',
            name='developers_board',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='%(class)s_developers_board', to='app.board'),
        ),
        migrations.AddField(
            model_name='tenant',
            name='operators_board',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='%(class)s_operators_board', to='app.board'),
        ),
    ]