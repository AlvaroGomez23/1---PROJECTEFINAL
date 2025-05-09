# Generated by Django 5.1.7 on 2025-04-24 14:38

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0010_book_exchange_count'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='reviewer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='book_reviews_given', to=settings.AUTH_USER_MODEL),
        ),
    ]
