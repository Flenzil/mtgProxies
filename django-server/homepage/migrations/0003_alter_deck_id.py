# Generated by Django 5.0.7 on 2024-07-25 12:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homepage', '0002_deck_delete_card'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deck',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
