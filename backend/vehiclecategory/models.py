from django.db import models

# Create your models here.

class VehicleCategory(models.Model):
    name = models.CharField(max_length=50)
    active = models.BooleanField(default=True)
    created_by = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_by = models.IntegerField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'vehiclecategory'
        verbose_name = 'Vehicle Category'
        verbose_name_plural = 'Vehicle Categories'

    def __str__(self):
        return self.name
