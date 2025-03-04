from django.contrib import admin
from .models import Contact,CurrentWeatherCondition,FutureWeather16dayspredictionModel 
# Register your models here.
admin.site.register(Contact)
admin.site.register(CurrentWeatherCondition)
admin.site.register(FutureWeather16dayspredictionModel)
# Customize the admin panel headers
admin.site.site_header = "My Real-Time Weather Forecasting Website | Admin Panel"
admin.site.site_title = "Admin Panel"
