# Generated by Django 5.2 on 2025-06-10 01:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoice', '0002_invoice_reference'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='reference',
            field=models.TextField(blank=True, help_text='Información adicional (Depósito de seguridad para extranjero, 50% del costo del alquiler, etc.).', verbose_name='referencia o código de transacción'),
        ),
    ]
