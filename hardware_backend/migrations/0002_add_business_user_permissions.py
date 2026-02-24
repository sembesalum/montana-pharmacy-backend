# Generated manually for manager-editable user permissions

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hardware_backend', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='businessuser',
            name='permissions',
            field=models.JSONField(blank=True, default=None, null=True),
        ),
    ]
