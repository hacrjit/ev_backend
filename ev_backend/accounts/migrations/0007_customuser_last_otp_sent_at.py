# Generated by Django 5.2 on 2025-04-29 06:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_alter_customuser_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='last_otp_sent_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
