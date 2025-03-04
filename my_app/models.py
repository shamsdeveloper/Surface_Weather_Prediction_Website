from django.db import models
class Contact(models.Model):
    name=models.CharField(max_length=250)
    email=models.EmailField()
    Phone_number=models.CharField(max_length=250)
    message=models.TextField()
    added_on=models.DateTimeField(auto_now_add=True)
    is_approved=models.BooleanField(default=True)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural="Contact Table"
#########################################################################
class CurrentWeatherCondition(models.Model):
    location_city_name = models.CharField(max_length=100, verbose_name="Location City Name")
    weather_condition = models.CharField(max_length=200, verbose_name="Weather Condition")
    weather_temperature = models.CharField(max_length=50, verbose_name="Weather Temperature")
    humidity = models.CharField(max_length=50, verbose_name="Humidity")
    pressure = models.CharField(max_length=50, verbose_name="Pressure")
    wind_speed = models.CharField(max_length=50, verbose_name="Wind Speed")
    cloudiness = models.CharField(max_length=50, verbose_name="Cloudiness")
    sunrise = models.CharField(max_length=50, verbose_name="Sunrise")
    sunset = models.CharField(max_length=50, verbose_name="Sunset")
    country = models.CharField(max_length=50, verbose_name="Country")
    wave_period = models.CharField(max_length=50, verbose_name="Wave Period")
    wavelength = models.CharField(max_length=50, verbose_name="Wavelength")
    wave_depth = models.CharField(max_length=50, verbose_name="Wave Depth")
    def __str__(self):
        return self.location_city_name
    class Meta:
        verbose_name_plural="CurrentWeatherCondition Table"
#############################################################################################
class FutureWeather16dayspredictionModel(models.Model):
    city_name = models.CharField(max_length=100)
    description = models.TextField()
    weather_main = models.CharField(max_length=50)
    weather_description = models.CharField(max_length=100)
    temp = models.FloatField()
    feels_like = models.FloatField()
    temp_min = models.FloatField()
    temp_max = models.FloatField()
    pressure = models.IntegerField()
    humidity = models.IntegerField()
    wind_speed = models.FloatField()
    wind_deg = models.IntegerField()
    rain_1h = models.FloatField()
    cloudiness = models.IntegerField()
    sunrise = models.TimeField()
    sunset = models.TimeField()
    timezone = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    wave_period = models.FloatField()
    wavelength = models.FloatField()
    wave_depth = models.FloatField()

    def __str__(self):
        return f"{self.city_name} - {self.sunrise}"
    class Meta:
        verbose_name_plural="Future16DaysWeatherCondition Table"