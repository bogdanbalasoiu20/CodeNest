# Generated by Django 5.1.1 on 2025-05-12 18:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('code_nest', '0016_test_updated_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='testresult',
            name='cooldown_until',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
