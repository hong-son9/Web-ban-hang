# Generated by Django 4.2.3 on 2023-07-15 09:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0002_product_image'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Oder',
            new_name='Order',
        ),
        migrations.RenameModel(
            old_name='Oder_item',
            new_name='Order_item',
        ),
        migrations.RenameField(
            model_name='order_item',
            old_name='oder',
            new_name='order',
        ),
    ]
