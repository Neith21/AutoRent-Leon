# Generated by Django 5.2 on 2025-06-07 16:53

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('branch', '0001_initial'),
        ('customer', '0001_initial'),
        ('vehicle', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Rental',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateTimeField(error_messages={'required': 'La fecha de inicio es obligatoria.'}, help_text='Momento exacto en que inicia el alquiler.', verbose_name='fecha y hora de inicio')),
                ('end_date', models.DateTimeField(error_messages={'required': 'La fecha de fin es obligatoria.'}, help_text='Momento exacto en que debe finalizar el alquiler.', verbose_name='fecha y hora de fin')),
                ('actual_return_date', models.DateTimeField(blank=True, help_text='Momento exacto en que el vehículo fue devuelto (se llena al finalizar).', null=True, verbose_name='fecha y hora de devolución real')),
                ('status', models.CharField(choices=[('Reservado', 'Reservado'), ('Activo', 'Activo'), ('Finalizado', 'Finalizado'), ('Retrasado', 'Retrasado'), ('Cancelado', 'Cancelado')], default='Reservado', help_text='Estado actual del proceso de alquiler.', max_length=20, verbose_name='estado del alquiler')),
                ('total_price', models.DecimalField(decimal_places=2, error_messages={'invalid': 'Ingrese un precio válido.', 'required': 'El precio total es obligatorio.'}, help_text='Costo total del alquiler por los días solicitados.', max_digits=10, validators=[django.core.validators.MinValueValidator(0.01)], verbose_name='precio total calculado')),
                ('fuel_level_pickup', models.CharField(choices=[('Vacio', 'Vacío'), ('1/4', '1/4'), ('1/2', '1/2'), ('3/4', '3/4'), ('Lleno', 'Lleno')], error_messages={'required': 'Debe especificar el nivel de combustible en la recogida.'}, help_text='Nivel de combustible al momento de entregar el vehículo.', max_length=10, verbose_name='nivel de combustible (recogida)')),
                ('fuel_level_return', models.CharField(blank=True, choices=[('Vacio', 'Vacío'), ('1/4', '1/4'), ('1/2', '1/2'), ('3/4', '3/4'), ('Lleno', 'Lleno')], help_text='Nivel de combustible al momento de recibir el vehículo.', max_length=10, null=True, verbose_name='nivel de combustible (devolución)')),
                ('remarks', models.TextField(blank=True, help_text='Notas o comentarios adicionales sobre el alquiler (daños, acuerdos, etc.).', null=True, verbose_name='observaciones')),
                ('active', models.BooleanField(default=True, verbose_name='activo')),
                ('created_by', models.IntegerField(blank=True, null=True, verbose_name='creado por')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='fecha de creación')),
                ('modified_by', models.IntegerField(blank=True, null=True, verbose_name='modificado por')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='última modificación')),
                ('customer', models.ForeignKey(error_messages={'required': 'Debe seleccionar un cliente.'}, help_text='Cliente que realiza el alquiler.', on_delete=django.db.models.deletion.RESTRICT, to='customer.customer', verbose_name='cliente')),
                ('pickup_branch', models.ForeignKey(error_messages={'required': 'Debe seleccionar una sucursal de recogida.'}, help_text='Sucursal donde el cliente recogerá el vehículo.', on_delete=django.db.models.deletion.RESTRICT, related_name='pickup_rentals', to='branch.branch', verbose_name='sucursal de recogida')),
                ('return_branch', models.ForeignKey(error_messages={'required': 'Debe seleccionar una sucursal de devolución.'}, help_text='Sucursal donde el cliente devolverá el vehículo.', on_delete=django.db.models.deletion.RESTRICT, related_name='return_rentals', to='branch.branch', verbose_name='sucursal de devolución')),
                ('vehicle', models.ForeignKey(error_messages={'required': 'Debe seleccionar un vehículo.'}, help_text='Vehículo a alquilar.', on_delete=django.db.models.deletion.RESTRICT, to='vehicle.vehicle', verbose_name='vehículo')),
            ],
            options={
                'verbose_name': 'Alquiler',
                'verbose_name_plural': 'Alquileres',
                'db_table': 'rental',
            },
        ),
    ]
