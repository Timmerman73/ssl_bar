# Generated by Django 4.1.7 on 2023-03-21 13:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BarApp', '0007_drankjes_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='drankjes',
            name='img',
            field=models.ImageField(blank=True, upload_to='media/'),
        ),
    ]
