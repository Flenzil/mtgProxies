# Generated by Django 5.0.7 on 2024-07-26 16:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('homepage', '0011_rename_random_basic_lands_params_random_basic_land_art'),
    ]

    operations = [
        migrations.RenameField(
            model_name='params',
            old_name='only_full_art_lands',
            new_name='only_full_art_basi_lands',
        ),
    ]
