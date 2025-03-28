# Generated by Django 5.1.7 on 2025-03-26 09:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_alter_resourceneed_donation_days_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='DonationDay',
            fields=[
                ('did', models.AutoField(primary_key=True, serialize=False)),
                ('day', models.CharField(max_length=10, unique=True)),
            ],
        ),
        migrations.AlterField(
            model_name='resourceneed',
            name='resource',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.resource'),
        ),
    ]
