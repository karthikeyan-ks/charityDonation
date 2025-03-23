# Generated by Django 5.1.7 on 2025-03-16 18:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_customuser_user_type_alter_customuser_email_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='is_test_user',
            field=models.BooleanField(default=False, help_text='Flag to identify test/dummy accounts'),
        ),
    ]
