from django.contrib import admin
from django.urls import path
from my_app import views as my_views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('Home/',my_views.Home,name='Home'),
    path('about_us/',my_views.about_us,name='about_us'),
    path('my-services/',my_views.Services,name='Services'),
    path('my_contact/',my_views.contact,name='contact'),
    path('my_Home_Admin/',my_views.Home_Admin,name='Home_Admin'),
    path('myadminaccount/',my_views.Register,name="Register"),
    path('admin_login/',my_views.SignIn,name="SignIn"),
    path('',my_views.My_Admin_Dashboard,name="My_Admin_Dashboard"),
    path('my-first-country/',my_views.Country1,name='Country1'),
    path('my-second-country/',my_views.Country2,name='Country2'),
    path('my-third-country/',my_views.Country3,name='Country3'),
    path('my-fourth-country/',my_views.Country5,name='Country5'),
    path('my-fifth-country/',my_views.Country6,name='Country6'),
    path('my-sixth-country/',my_views.Country7,name='Country7'),
    ##############################################################################
    path('my-current-country/',my_views.Country4,name='Country4'),
    path('adminlogout/',my_views.adminlogout, name="adminlogout"),
    path('save_weather_condition/',my_views.save_weather_condition, name='save_weather_condition'),
    path('view_weather_condition/',my_views.View_all_current,name='View_all_current'),
    ##########################################################################################
    path('weather-forecast/',my_views.weather_forecast_view, name='weather_forecast_view'),
    path('weather-forecast1/',my_views.weather_forecast_view1, name='weather_forecast_view1'),
    ######################################################################################################
    path('future-weather-forecast1/',my_views.My_Future, name='My_Future'),


]
