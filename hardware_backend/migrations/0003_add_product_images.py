# Generated manually for product images (up to 3)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hardware_backend', '0002_add_business_user_permissions'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='images',
            field=models.JSONField(blank=True, default=None, null=True),
        ),
    ]
