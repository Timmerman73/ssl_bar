# Generated by Django 4.1.7 on 2023-03-21 13:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BarApp', '0012_alter_drankjes_img'),
    ]

    operations = [
        migrations.AlterField(
            model_name='drankjes',
            name='img',
            field=models.ImageField(upload_to='media'),
        ),
    ]