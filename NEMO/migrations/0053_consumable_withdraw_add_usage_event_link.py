# Generated by Django 3.2.20 on 2023-08-28 17:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('NEMO', '0052_area_add_auto_logout_time'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='consumablewithdraw',
            name='tool_usage',
        ),
        migrations.AddField(
            model_name='consumablewithdraw',
            name='usage_event',
            field=models.ForeignKey(blank=True, help_text='Whether this withdraw is from tool usage', null=True, on_delete=django.db.models.deletion.CASCADE, to='NEMO.usageevent'),
        ),
    ]
