# Generated by Django 4.0.4 on 2022-05-25 00:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0049_alter_label_table'),
    ]

    operations = [
        migrations.CreateModel(
            name='AttachmentAssociation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attachment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_attachment', to='app.attachment')),
            ],
            options={
                'db_table': 'attachment_association',
            },
        ),
        migrations.RenameField(
            model_name='issue',
            old_name='association',
            new_name='associations',
        ),
        migrations.RemoveField(
            model_name='issue',
            name='attachments',
        ),
        migrations.AddField(
            model_name='issue',
            name='attachments',
            field=models.ManyToManyField(blank=True, through='app.AttachmentAssociation', to='app.attachment'),
        ),
        migrations.AddField(
            model_name='attachmentassociation',
            name='issue',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_issue', to='app.issue'),
        ),
    ]