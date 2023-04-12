# Generated by Django 3.2.5 on 2021-10-08 11:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0005_add_products_to_order_as_mtm'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='products',
            field=models.ManyToManyField(related_name='orders', through='shop.OrderedProduct', to='shop.Product'),
        ),
    ]
