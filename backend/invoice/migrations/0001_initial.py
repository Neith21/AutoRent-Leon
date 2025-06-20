# Generated by Django 5.2 on 2025-06-07 16:53

import django.core.validators
import django.db.models.deletion
import django.utils.timezone
import invoice.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('rental', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invoice_number', models.CharField(default=invoice.models.generate_invoice_number, error_messages={'unique': 'Este número de factura ya existe.'}, help_text='Código único de la factura. Se genera automáticamente.', max_length=50, unique=True, verbose_name='número de factura')),
                ('issue_date', models.DateTimeField(default=django.utils.timezone.now, help_text='Momento en que se emite la factura.', verbose_name='fecha y hora de emisión')),
                ('total_amount', models.DecimalField(decimal_places=2, error_messages={'invalid': 'Ingrese un monto válido.', 'required': 'El monto total es obligatorio.'}, help_text='El costo total facturado, incluyendo todos los cargos.', max_digits=10, validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='monto total de la factura')),
                ('status', models.CharField(choices=[('Emitida', 'Emitida'), ('Pagada', 'Pagada'), ('Anulada', 'Anulada')], default='Emitida', help_text='Estado actual de la factura (emitida, pagada, anulada).', max_length=20, verbose_name='estado de la factura')),
                ('active', models.BooleanField(default=True, verbose_name='activo')),
                ('created_by', models.IntegerField(blank=True, null=True, verbose_name='creado por')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='fecha de creación')),
                ('modified_by', models.IntegerField(blank=True, null=True, verbose_name='modificado por')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='última modificación')),
                ('rental', models.OneToOneField(error_messages={'required': 'La factura debe estar asociada a un alquiler.'}, help_text='El alquiler que genera esta factura.', on_delete=django.db.models.deletion.CASCADE, to='rental.rental', verbose_name='alquiler asociado')),
            ],
            options={
                'verbose_name': 'Factura',
                'verbose_name_plural': 'Facturas',
                'db_table': 'invoice',
                'ordering': ['-issue_date'],
            },
        ),
    ]
