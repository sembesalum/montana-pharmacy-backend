# Generated manually to add missing fields to Product model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hardware_backend', '0007_add_sales_models'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='minimum_stock',
            field=models.IntegerField(default=10),
        ),
        migrations.AddField(
            model_name='product',
            name='expiry_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
