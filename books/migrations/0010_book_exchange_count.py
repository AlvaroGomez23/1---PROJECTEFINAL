# Generated by Django 5.1.7 on 2025-04-10 14:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0009_alter_book_isbn'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='exchange_count',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
