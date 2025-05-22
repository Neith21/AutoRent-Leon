from django.db import models
from vehicle.models import Vehicle

# Create your models here.

class VehicleImage(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='images')
    vehicle_image = models.CharField(max_length=255)

    class Meta:
        db_table = 'vehicleimage'
        verbose_name = 'Vehicle Image'
        verbose_name_plural = 'Vehicle Images'

    def __str__(self):
        return f"Image for {self.vehicle.plate}"