# Generated by Django 5.2 on 2025-06-07 16:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('vehicle', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='VehicleImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vehicle_image', models.CharField(max_length=255)),
                ('vehicle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='vehicle.vehicle')),
            ],
            options={
                'verbose_name': 'Vehicle Image',
                'verbose_name_plural': 'Vehicle Images',
                'db_table': 'vehicleimage',
            },
        ),
    ]
