# Generated manually to add sales functionality models

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hardware_backend', '0006_customer_shelf_order_salesperson_and_more'),
    ]

    operations = [
        # Add new models only - don't modify existing ones
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('customer_id', models.CharField(default='CUST_', max_length=50, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('phone', models.CharField(max_length=20)),
                ('email', models.EmailField(blank=True, null=True)),
                ('address', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'customers',
            },
        ),
        migrations.CreateModel(
            name='Shelf',
            fields=[
                ('shelf_id', models.CharField(default='SHELF_', max_length=50, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'shelves',
            },
        ),
        migrations.CreateModel(
            name='ProductLocation',
            fields=[
                ('location_id', models.CharField(default='LOC_', max_length=50, primary_key=True, serialize=False)),
                ('quantity', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='locations', to='hardware_backend.product')),
                ('shelf', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='hardware_backend.shelf')),
            ],
            options={
                'db_table': 'product_locations',
            },
        ),
        migrations.CreateModel(
            name='Sale',
            fields=[
                ('sale_id', models.CharField(default='SALE_', max_length=50, primary_key=True, serialize=False)),
                ('customer_name', models.CharField(blank=True, max_length=200, null=True)),
                ('customer_phone', models.CharField(blank=True, max_length=20, null=True)),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('discount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('payment_method', models.CharField(choices=[('CASH', 'Cash'), ('CARD', 'Card'), ('MOBILE_MONEY', 'Mobile Money'), ('BANK_TRANSFER', 'Bank Transfer')], default='CASH', max_length=20)),
                ('payment_status', models.CharField(choices=[('PAID', 'Paid'), ('UNPAID', 'Unpaid'), ('PARTIAL', 'Partially Paid')], default='PAID', max_length=20)),
                ('salesperson_name', models.CharField(blank=True, max_length=200, null=True)),
                ('sale_date', models.DateTimeField(auto_now_add=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('customer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sales', to='hardware_backend.customer')),
                ('salesperson', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sales', to='hardware_backend.businessuser')),
            ],
            options={
                'db_table': 'sales',
                'ordering': ['-sale_date'],
            },
        ),
        migrations.CreateModel(
            name='SaleItem',
            fields=[
                ('sale_item_id', models.CharField(default='ITEM_', max_length=50, primary_key=True, serialize=False)),
                ('product_name', models.CharField(max_length=200)),
                ('quantity', models.PositiveIntegerField()),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sale_items', to='hardware_backend.product')),
                ('sale', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='hardware_backend.sale')),
            ],
            options={
                'db_table': 'sale_items',
            },
        ),
        migrations.AddConstraint(
            model_name='productlocation',
            constraint=models.UniqueConstraint(fields=('product', 'shelf'), name='unique_product_shelf'),
        ),
    ]
