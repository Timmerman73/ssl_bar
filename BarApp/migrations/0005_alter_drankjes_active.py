# Generated by Django 4.1 on 2023-03-23 22:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BarApp', '0004_alter_drankjes_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='drankjes',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]