from django.db import models
from brand.models import Brand

# Create your models here.

class VehicleModel(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.RESTRICT)
    name = models.CharField(max_length=100)
    active = models.BooleanField(default=True)
    created_by = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_by = models.IntegerField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'vehiclemodel'
        verbose_name = 'Vehicle Model'
        verbose_name_plural = 'Vehicle Models'

    def __str__(self):
        return f"{self.brand.name} {self.name}"