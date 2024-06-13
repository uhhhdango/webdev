from django.db import models

class OceanData(models.Model):
    source = models.CharField(max_length=50, default='Unknown')
    latitude = models.FloatField()
    longitude = models.FloatField()
    time = models.DateTimeField()
    depth = models.FloatField()
    temperature = models.FloatField(null=True, blank=True)
    salinity = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.source} - {self.time}"
