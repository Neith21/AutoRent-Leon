# Generated by Django 5.2 on 2025-06-12 16:55

import django.core.validators
import django.db.models.deletion
import simple_history.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('brand', '0002_historicalbrand'),
        ('vehiclemodel', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalVehicleModel',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('name', models.CharField(error_messages={'blank': 'El nombre del modelo no puede estar vacío.', 'max_length': 'El nombre del modelo no puede tener más de 100 caracteres.', 'required': 'El nombre del modelo es obligatorio.', 'unique': 'Ya existe un modelo con este nombre para esta marca.'}, help_text='Nombre del modelo del vehículo (ej. Corolla, Hilux, Civic). Máx. 100 caracteres.', max_length=100, validators=[django.core.validators.RegexValidator(message='El nombre del modelo solo puede contener letras, números, espacios, guiones (-) y puntos (.).', regex='^[a-zA-Z0-9ñÑáéíóúÁÉÍÓÚüÜ\\s\\-\\.]+$')], verbose_name='nombre del modelo')),
                ('active', models.BooleanField(default=True, verbose_name='activo')),
                ('created_by', models.IntegerField(blank=True, null=True, verbose_name='creado por')),
                ('created_at', models.DateTimeField(blank=True, editable=False, verbose_name='fecha de creación')),
                ('modified_by', models.IntegerField(blank=True, null=True, verbose_name='modificado por')),
                ('updated_at', models.DateTimeField(blank=True, editable=False, verbose_name='última modificación')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('brand', models.ForeignKey(blank=True, db_constraint=False, error_messages={'blank': 'La marca no puede estar en blanco.', 'invalid_choice': 'La marca seleccionada no es válida.', 'null': 'La marca no puede estar vacía.', 'required': 'Debe seleccionar una marca.'}, help_text='Seleccione la marca del modelo del vehículo.', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='brand.brand', verbose_name='marca')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical Modelo de Vehículo',
                'verbose_name_plural': 'historical Modelos de Vehículos',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
