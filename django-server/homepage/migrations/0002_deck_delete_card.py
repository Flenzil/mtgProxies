# Generated by Django 5.0.7 on 2024-07-24 16:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homepage', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Deck',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('name', models.TextField()),
                ('set_code', models.TextField()),
                ('collecter_number', models.TextField()),
            ],
        ),
        migrations.DeleteModel(
            name='Card',
        ),
    ]
