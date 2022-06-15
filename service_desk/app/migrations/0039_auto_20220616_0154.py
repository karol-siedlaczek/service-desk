# Generated by Django 3.2.13 on 2022-06-15 23:54

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0038_remove_status_backward_transition_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='AttachmentAssociation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'db_table': 'attachment_association',
            },
        ),
        migrations.CreateModel(
            name='LabelAssociation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'db_table': 'label_association',
            },
        ),
        migrations.CreateModel(
            name='TenantSession',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('active', models.BooleanField(default=False, editable=False)),
                ('user_type', models.CharField(choices=[('customer', 'Customer'), ('operator', 'Operator'), ('developer', 'Developer')], max_length=25)),
            ],
            options={
                'verbose_name': 'tenant session',
                'verbose_name_plural': 'tenant sessions',
                'db_table': 'tenant_session',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Transition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=55)),
            ],
            options={
                'verbose_name': 'transition',
                'verbose_name_plural': 'transitions',
                'db_table': 'transition',
                'ordering': ['src_status'],
            },
        ),
        migrations.CreateModel(
            name='TransitionAssociation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'transition association',
                'verbose_name_plural': 'transition associations',
                'db_table': 'transition_association',
                'ordering': ['transition'],
            },
        ),
        migrations.AlterModelOptions(
            name='status',
            options={'ordering': ['name'], 'verbose_name': 'status', 'verbose_name_plural': 'statuses'},
        ),
        migrations.AlterModelOptions(
            name='tenant',
            options={'ordering': ['id'], 'permissions': [('view_customer_space', 'Manage tenant as customer'), ('view_operator_space', 'Manage tenant as operator'), ('view_developer_space', 'Manage tenant as developer')], 'verbose_name': 'tenant', 'verbose_name_plural': 'tenants'},
        ),
        migrations.RemoveField(
            model_name='issue',
            name='association',
        ),
        migrations.RemoveField(
            model_name='issue',
            name='label',
        ),
        migrations.RemoveField(
            model_name='status',
            name='board_column',
        ),
        migrations.RemoveField(
            model_name='status',
            name='step',
        ),
        migrations.AddField(
            model_name='boardcolumn',
            name='statuses',
            field=models.ManyToManyField(through='app.BoardColumnAssociation', to='app.Status'),
        ),
        migrations.AddField(
            model_name='issue',
            name='associations',
            field=models.ManyToManyField(related_name='_app_issue_associations_+', through='app.IssueAssociation', to='app.Issue'),
        ),
        migrations.AddField(
            model_name='issue',
            name='slug',
            field=models.SlugField(blank=True, max_length=55),
        ),
        migrations.AlterField(
            model_name='attachment',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to='F:\\Programs\\Repository\\Python\\Private\\GitHub\\service-desk\\service_desk/media/attachments', validators=[django.core.validators.FileExtensionValidator]),
        ),
        migrations.AlterField(
            model_name='board',
            name='env_type',
            field=models.CharField(blank=True, choices=[('service-desk', 'Service Desk'), ('software', 'Software')], max_length=50, null=True, verbose_name='Environment type'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='created',
            field=models.DateTimeField(blank=True, help_text='Date when comment created', verbose_name='Created'),
        ),
        migrations.RemoveField(
            model_name='issue',
            name='attachments',
        ),
        migrations.AlterField(
            model_name='issue',
            name='comments',
            field=models.ManyToManyField(blank=True, through='app.CommentAssociation', to='app.Comment'),
        ),
        migrations.AlterField(
            model_name='issue',
            name='description',
            field=tinymce.models.HTMLField(blank=True, help_text='Describe the issue', null=True, verbose_name='description'),
        ),
        migrations.AlterField(
            model_name='issue',
            name='key',
            field=models.CharField(editable=False, max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='issue',
            name='priority',
            field=models.ForeignKey(default=3, on_delete=django.db.models.deletion.CASCADE, related_name='issue_priority', to='app.priority'),
        ),
        migrations.AlterField(
            model_name='issue',
            name='status',
            field=models.ForeignKey(blank=True, default=15, on_delete=django.db.models.deletion.CASCADE, related_name='issue_status', to='app.status'),
        ),
        migrations.AlterField(
            model_name='issue',
            name='suspended',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='issue',
            name='type',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='issue_type', to='app.issuetype'),
        ),
        migrations.AlterField(
            model_name='issuetype',
            name='env_type',
            field=models.CharField(choices=[('service-desk', 'Service Desk'), ('software', 'Software')], max_length=50, null=True, verbose_name='Environment type'),
        ),
        migrations.AlterField(
            model_name='issuetype',
            name='icon',
            field=models.ImageField(blank=True, max_length=500, upload_to='F:\\Programs\\Repository\\Python\\Private\\GitHub\\service-desk\\service_desk/media/img/issue_type', validators=[django.core.validators.FileExtensionValidator]),
        ),
        migrations.AlterField(
            model_name='priority',
            name='icon',
            field=models.ImageField(blank=True, max_length=500, upload_to='F:\\Programs\\Repository\\Python\\Private\\GitHub\\service-desk\\service_desk/media/img/priority', validators=[django.core.validators.FileExtensionValidator]),
        ),
        migrations.AlterField(
            model_name='tenant',
            name='count',
            field=models.PositiveIntegerField(default=0, editable=False, help_text='Number of issues'),
        ),
        migrations.AlterField(
            model_name='tenant',
            name='icon',
            field=models.ImageField(blank=True, max_length=500, upload_to='F:\\Programs\\Repository\\Python\\Private\\GitHub\\service-desk\\service_desk/media/img/tenant', validators=[django.core.validators.FileExtensionValidator]),
        ),
        migrations.AlterField(
            model_name='tenant',
            name='key',
            field=models.CharField(max_length=50, unique=True),
        ),
        migrations.AlterModelTable(
            name='attachment',
            table='attachment',
        ),
        migrations.AlterModelTable(
            name='comment',
            table='comment',
        ),
        migrations.AlterModelTable(
            name='label',
            table='label',
        ),
        migrations.AlterModelTable(
            name='priority',
            table='priority',
        ),
        migrations.AlterModelTable(
            name='resolution',
            table='resolution',
        ),
        migrations.AlterModelTable(
            name='status',
            table='status',
        ),
        migrations.DeleteModel(
            name='StatusAssociation',
        ),
        migrations.AddField(
            model_name='transitionassociation',
            name='issue_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transitionassociation_issue_type', to='app.issuetype'),
        ),
        migrations.AddField(
            model_name='transitionassociation',
            name='transition',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transitionassociation_transition', to='app.transition'),
        ),
        migrations.AddField(
            model_name='transition',
            name='dest_status',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transition_dest_status', to='app.status'),
        ),
        migrations.AddField(
            model_name='transition',
            name='src_status',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transition_src_status', to='app.status'),
        ),
        migrations.AddField(
            model_name='tenantsession',
            name='tenant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tenantsession_tenant', to='app.tenant'),
        ),
        migrations.AddField(
            model_name='tenantsession',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tenantsession_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='labelassociation',
            name='issue',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='labelassociation_issue', to='app.issue'),
        ),
        migrations.AddField(
            model_name='labelassociation',
            name='label',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='labelassociation_label', to='app.label'),
        ),
        migrations.AddField(
            model_name='attachmentassociation',
            name='attachment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attachmentassociation_attachment', to='app.attachment'),
        ),
        migrations.AddField(
            model_name='attachmentassociation',
            name='issue',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attachmentassociation_issue', to='app.issue'),
        ),
        migrations.AddField(
            model_name='issue',
            name='labels',
            field=models.ManyToManyField(blank=True, through='app.LabelAssociation', to='app.Label'),
        ),
        migrations.AddField(
            model_name='status',
            name='transitions',
            field=models.ManyToManyField(related_name='_app_status_transitions_+', through='app.Transition', to='app.Status'),
        ),
        migrations.AddField(
            model_name='issue',
            name='attachments',
            field=models.ManyToManyField(blank=True, through='app.AttachmentAssociation', to='app.Attachment'),
        ),
        migrations.AlterUniqueTogether(
            name='transitionassociation',
            unique_together={('issue_type', 'transition')},
        ),
    ]
