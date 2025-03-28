# Generated by Django 5.1.7 on 2025-03-26 09:01

import django.db.models.deletion
import multiselectfield.db.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_alter_resourceneed_donation_days'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resourceneed',
            name='donation_days',
            field=multiselectfield.db.fields.MultiSelectField(choices=[('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'), ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday'), ('Sunday', 'Sunday')], max_length=50),
        ),
        migrations.RemoveField(
            model_name='resourceneed',
            name='resource',
        ),
        migrations.AddField(
            model_name='resourceneed',
            name='resource',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='users.resource'),
        ),
    ]
