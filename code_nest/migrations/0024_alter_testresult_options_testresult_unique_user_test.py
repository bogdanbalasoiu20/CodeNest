# Generated by Django 5.1.1 on 2025-05-13 12:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('code_nest', '0023_alter_testresult_unique_together'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='testresult',
            options={},
        ),
        migrations.AddConstraint(
            model_name='testresult',
            constraint=models.UniqueConstraint(fields=('user', 'test'), name='unique_user_test'),
        ),
    ]
