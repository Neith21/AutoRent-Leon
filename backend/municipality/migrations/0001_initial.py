# Generated by Django 5.2 on 2025-06-07 16:53

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('department', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Municipality',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(error_messages={'unique': 'Ya existe un municipio con este código.'}, help_text='Código numérico único de hasta 8 dígitos para el municipio.', max_length=8, unique=True, validators=[django.core.validators.RegexValidator(message='El código de municipio solo puede contener números.', regex='^[0-9]+$')], verbose_name='código de municipio')),
                ('municipality', models.CharField(error_messages={'blank': 'El nombre del municipio no puede estar vacío.', 'required': 'El nombre del municipio es obligatorio.'}, help_text="Nombre oficial del municipio. Solo se permiten letras, números, espacios y los caracteres: - . , # & ( ) '", max_length=255, validators=[django.core.validators.RegexValidator(message="El nombre del municipio solo puede contener letras, números, espacios y los siguientes caracteres especiales: - . , # & ( ) '", regex="^[a-zA-Z0-9\\s\\-\\.,#&()\\'ñÑáéíóúÁÉÍÓÚ]+$")], verbose_name='nombre del municipio')),
                ('active', models.BooleanField(default=True, verbose_name='activo')),
                ('created_by', models.IntegerField(blank=True, null=True, verbose_name='ID del creador')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='fecha de creación')),
                ('modified_by', models.IntegerField(blank=True, null=True, verbose_name='ID del modificador')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='última modificación')),
                ('department', models.ForeignKey(error_messages={'invalid_choice': 'El departamento seleccionado no es válido.', 'required': 'Debe seleccionar un departamento.'}, help_text='Departamento al que está asociado este municipio.', on_delete=django.db.models.deletion.CASCADE, related_name='municipalities', to='department.department', verbose_name='departamento al que pertenece')),
            ],
            options={
                'verbose_name': 'Municipio',
                'verbose_name_plural': 'Municipios',
                'db_table': 'municipality',
                'ordering': ['department', 'municipality'],
            },
        ),
    ]
