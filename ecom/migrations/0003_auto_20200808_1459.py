# Generated by Django 3.0.8 on 2020-08-08 09:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecom', '0002_auto_20200808_1332'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='name',
            field=models.CharField(max_length=200),
        ),
    ]