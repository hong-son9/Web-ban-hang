# Generated by Django 4.2.3 on 2023-07-16 09:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0007_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='category',
            field=models.ManyToManyField(related_name='product', to='apps.category'),
        ),
    ]