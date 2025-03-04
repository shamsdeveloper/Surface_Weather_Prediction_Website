from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Contact
from .models import *
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.urls import reverse
import matplotlib
matplotlib.use('Agg')  # Set non-interactive backend
from django.views.decorators.csrf import csrf_exempt
import requests
import numpy as np
import plotly.graph_objects as go
from datetime import datetime as dt
from django.http import JsonResponse
from django.db import IntegrityError
# from Machine_Learning_Weather_Prediction_Code import WeatherPrediction
from .models import CurrentWeatherCondition,FutureWeather16dayspredictionModel
from django.http import JsonResponse
import pandas as pd
import plotly.express as px
import shutil
from django.http import HttpResponse
##################################################################################
def Home(request):
    return render(request,'home.html')
def about_us(request):
    return render(request,'about.html')
def Services(request):
    return render(request,'services.html')
#######################################################################################
def contact(request):
    if request.method == "POST":
        # Retrieve form data
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        message = request.POST.get('message')
        
        # Save data to the database
        contact_record = Contact(
            name=name,
            email=email,
            Phone_number=phone,
            message=message
        )
        contact_record.save()
        # Add a success message
        messages.success(request, "Your message has been submitted successfully!")
        return redirect('contact')  # Redirect to the contact page
    return render(request,'contact.html')
#######################################################################################
def Home_Admin(request):
    return render(request,'home_admin.html')
##########################################################################################
def Register(request):
    if request.method == 'POST':
        first_name1 = request.POST['fname']
        last_name1 = request.POST['lname']
        mobile_number = request.POST['number']
        email_addres = request.POST['email']
        user_password = request.POST['password']
        user_con_password = request.POST['cpassword']
        
        number_check = User.objects.filter(username=mobile_number).exists()
        email_check = User.objects.filter(email=email_addres).exists()
        
        if number_check:
            return redirect(f'/myadminaccount/?message=Your%20Number%20Already%20Exists&type=error')
        elif email_check:
            return redirect(f'/myadminaccount/?message=Your%20Email%20Already%20Exists&type=error')
        elif len(mobile_number)!=11:
            return redirect(f'/myadminaccount/?message=Number%20Should%20Be%2011%20Digit&type=error')
        elif user_password != user_con_password:
            return redirect(f'/myadminaccount/?message=Password%20And%20Confirm%20Didn\'t%20Match&type=error')
        else:
            user1=User.objects.create_user(username=mobile_number, email=email_addres, password=user_con_password)
            user1.first_name = first_name1
            user1.last_name = last_name1
            user1.save()
            return redirect(f'/admin_login/?message=Admin%20User%20Account%20is%20Created%20Successfully&type=success')
    return render(request, 'user/register.html')
#######################################################################
def SignIn(request):
    if request.method == 'POST':
        mobile_number = request.POST['username']
        email_addres = request.POST['email']
        user_password = request.POST['password']
        login_user_data = authenticate(request, username=mobile_number,password=user_password,email=email_addres)
        
        if login_user_data is not None:
            auth_login(request, login_user_data)
            message = "Successfully logged in!"
            message_type = "success"
            #########################################################
            # Get the count of current weather records
            total_current_weather_count = CurrentWeatherCondition.objects.count()
            
            # Count the unique cities in the future weather predictions
            total_future_weather_count = FutureWeather16dayspredictionModel.objects.values('city_name').distinct().count()
            return render(request, 'Dashboard/admin.html', 
                        {
                            'message': message, 'message_type': message_type,
                           'total_current_weather_count': total_current_weather_count,
                           'total_future_weather_count': total_future_weather_count
                        })
        else:
            message = "Please enter the correct details."
            message_type = "error"
            return render(request, 'user/login.html', {'message': message, 'message_type': message_type})
    return render(request, 'user/login.html')
################################################################################################################################################
def My_Admin_Dashboard(request):
    # Get the count of current weather records
    total_current_weather_count = CurrentWeatherCondition.objects.count()
    
    # Count the unique cities in the future weather predictions
    total_future_weather_count = FutureWeather16dayspredictionModel.objects.values('city_name').distinct().count()
    
    return render(request, 'Dashboard/admin.html', {
        'total_current_weather_count': total_current_weather_count,
        'total_future_weather_count': total_future_weather_count
    })

####################################################################################################################################################
def Country1(request):
    city = request.POST.get('city', 'Pahang')

    weather_url = f'https://api.openweathermap.org/data/2.5/weather'
    WEATHER_API_KEY = '39695639fa6ea8973a7ac6690056135b'
    weather_params = {'q': city, 'appid': WEATHER_API_KEY, 'units': 'metric'}

    SEARCH_ENGINE_ID = '040d46d9d92544fe7'
    API_KEY = 'AIzaSyDatm0RfUn7aVVKewPfSNXJXFa7qD84Shg'
    query = city + " landscape"
    page = 1
    start = (page - 1) * 10 + 1
    search_url = f"https://www.googleapis.com/customsearch/v1"
    search_params = {
        'key': API_KEY,
        'cx': SEARCH_ENGINE_ID,
        'q': query,
        'start': start,
        'searchType': 'image',
        'imgSize': 'large',
        'safe': 'active'
    }

    try:
        weather_data = requests.get(weather_url, params=weather_params).json()

        description = weather_data['weather'][0]['description']
        icon = weather_data['weather'][0]['icon']
        temp = weather_data['main']['temp']

        coord = weather_data['coord']
        wind = weather_data['wind']
        rain = weather_data.get('rain', {"1h": 0})
        clouds = weather_data['clouds']
        sys = weather_data['sys']

        day = dt.now().strftime('%d %B %Y')

        image_response = requests.get(search_url, params=search_params).json()
        search_items = image_response.get("items", [])

        if search_items:
            image_url = search_items[0]['link']
        else:
            image_url = None

        # Calculate wave properties
        temperature_celsius = temp
        wind_speed = wind['speed']

        g = 9.8
        T = 1 / np.sqrt(wind_speed)
        wavelength = (g * T**2) / (2 * np.pi)
        wave_depth = wavelength / (2 * np.pi)

        # Prepare data for plotting
        properties = ['Wind Speed (m/s)', 'Wave Period (s)', 'Wavelength (m)', 'Wave Depth (m)', 'Temperature (°C)']
        values = [wind_speed, T, wavelength, wave_depth, temperature_celsius]

        # Create modern line plot using Plotly
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=properties, y=values, mode='lines+markers',
                                 line=dict(color='blue', width=2),
                                 marker=dict(size=10, color='blue', symbol='circle')))
        fig.update_layout(
            title='Weather and Wave Properties',
            xaxis_title='Properties',
            yaxis_title='Values',
            template='plotly_white',
            font=dict(size=12),
            margin=dict(l=40, r=40, t=50, b=40)
        )

        # Convert plotly graph to HTML div string
        plot_html = fig.to_html(full_html=False, default_height=500)

        return render(request, 'Dashboard/weather1.html', {
            'description': description,
            'icon': icon,
            'temp': temp,
            'day': day,
            'city': city,
            'exception_occurred': False,
            'image_url': image_url,
            'plot_html': plot_html,

            # Additional weather data
            'coord_lat': coord['lat'],
            'coord_lon': coord['lon'],
            'weather_main': weather_data['weather'][0]['main'],
            'weather_description': weather_data['weather'][0]['description'],
            'feels_like': temperature_celsius,
            'temp_min': weather_data['main']['temp_min'],
            'temp_max': weather_data['main']['temp_max'],
            'pressure': weather_data['main']['pressure'],
            'humidity': weather_data['main']['humidity'],
            'wind_speed': wind_speed,
            'wind_deg': wind['deg'],
            'rain_1h': rain.get('1h', 0),
            'cloudiness': clouds['all'],
            'sunrise': dt.fromtimestamp(sys.get('sunrise', 0)).strftime('%H:%M:%S'),
            'sunset': dt.fromtimestamp(sys.get('sunset', 0)).strftime('%H:%M:%S'),
            'timezone': weather_data['timezone'],
            'country': sys['country'],
            'wave_period': T,
            'wavelength': wavelength,
            'wave_depth': wave_depth,
        })

    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        day = dt.now().strftime('%d %B %Y')
        return render(request, 'Dashboard/weather1.html', {
            'description': 'clear sky',
            'icon': '01d',
            'temp': 25,
            'day': day,
            'city': 'indore',
            'exception_occurred': True,
            'image_url': None,
            'plot_html': None,
        })
######################################################################################################################################
def Country2(request):
    city = request.POST.get('city', 'Johor')

    weather_url = f'https://api.openweathermap.org/data/2.5/weather'
    WEATHER_API_KEY = '39695639fa6ea8973a7ac6690056135b'
    weather_params = {'q': city, 'appid': WEATHER_API_KEY, 'units': 'metric'}

    SEARCH_ENGINE_ID = '040d46d9d92544fe7'
    API_KEY = 'AIzaSyDatm0RfUn7aVVKewPfSNXJXFa7qD84Shg'
    query = city + " landscape"
    page = 1
    start = (page - 1) * 10 + 1
    search_url = f"https://www.googleapis.com/customsearch/v1"
    search_params = {
        'key': API_KEY,
        'cx': SEARCH_ENGINE_ID,
        'q': query,
        'start': start,
        'searchType': 'image',
        'imgSize': 'large',
        'safe': 'active'
    }

    try:
        weather_data = requests.get(weather_url, params=weather_params).json()

        description = weather_data['weather'][0]['description']
        icon = weather_data['weather'][0]['icon']
        temp = weather_data['main']['temp']

        coord = weather_data['coord']
        wind = weather_data['wind']
        rain = weather_data.get('rain', {"1h": 0})
        clouds = weather_data['clouds']
        sys = weather_data['sys']

        day = dt.now().strftime('%d %B %Y')

        image_response = requests.get(search_url, params=search_params).json()
        search_items = image_response.get("items", [])

        if search_items:
            image_url = search_items[0]['link']
        else:
            image_url = None

        # Calculate wave properties
        temperature_celsius = temp
        wind_speed = wind['speed']

        g = 9.8
        T = 1 / np.sqrt(wind_speed)
        wavelength = (g * T**2) / (2 * np.pi)
        wave_depth = wavelength / (2 * np.pi)

        # Prepare data for plotting
        properties = ['Wind Speed (m/s)', 'Wave Period (s)', 'Wavelength (m)', 'Wave Depth (m)', 'Temperature (°C)']
        values = [wind_speed, T, wavelength, wave_depth, temperature_celsius]

        # Create modern line plot using Plotly
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=properties, y=values, mode='lines+markers',
                                 line=dict(color='blue', width=2),
                                 marker=dict(size=10, color='blue', symbol='circle')))
        fig.update_layout(
            title='Weather and Wave Properties',
            xaxis_title='Properties',
            yaxis_title='Values',
            template='plotly_white',
            font=dict(size=12),
            margin=dict(l=40, r=40, t=50, b=40)
        )

        # Convert plotly graph to HTML div string
        plot_html = fig.to_html(full_html=False, default_height=500)

        return render(request, 'Dashboard/weather2.html', {
            'description': description,
            'icon': icon,
            'temp': temp,
            'day': day,
            'city': city,
            'exception_occurred': False,
            'image_url': image_url,
            'plot_html': plot_html,

            # Additional weather data
            'coord_lat': coord['lat'],
            'coord_lon': coord['lon'],
            'weather_main': weather_data['weather'][0]['main'],
            'weather_description': weather_data['weather'][0]['description'],
            'feels_like': temperature_celsius,
            'temp_min': weather_data['main']['temp_min'],
            'temp_max': weather_data['main']['temp_max'],
            'pressure': weather_data['main']['pressure'],
            'humidity': weather_data['main']['humidity'],
            'wind_speed': wind_speed,
            'wind_deg': wind['deg'],
            'rain_1h': rain.get('1h', 0),
            'cloudiness': clouds['all'],
            'sunrise': dt.fromtimestamp(sys.get('sunrise', 0)).strftime('%H:%M:%S'),
            'sunset': dt.fromtimestamp(sys.get('sunset', 0)).strftime('%H:%M:%S'),
            'timezone': weather_data['timezone'],
            'country': sys['country'],
            'wave_period': T,
            'wavelength': wavelength,
            'wave_depth': wave_depth,
        })

    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        day = dt.now().strftime('%d %B %Y')
        return render(request, 'Dashboard/weather2.html', {
            'description': 'clear sky',
            'icon': '01d',
            'temp': 25,
            'day': day,
            'city': 'indore',
            'exception_occurred': True,
            'image_url': None,
            'plot_html': None,
        })
################################################################################################################
def Country3(request):
    city = request.POST.get('city', 'Terengganu')

    weather_url = f'https://api.openweathermap.org/data/2.5/weather'
    WEATHER_API_KEY = '39695639fa6ea8973a7ac6690056135b'
    weather_params = {'q': city, 'appid': WEATHER_API_KEY, 'units': 'metric'}

    SEARCH_ENGINE_ID = '040d46d9d92544fe7'
    API_KEY = 'AIzaSyDatm0RfUn7aVVKewPfSNXJXFa7qD84Shg'
    query = city + " landscape"
    page = 1
    start = (page - 1) * 10 + 1
    search_url = f"https://www.googleapis.com/customsearch/v1"
    search_params = {
        'key': API_KEY,
        'cx': SEARCH_ENGINE_ID,
        'q': query,
        'start': start,
        'searchType': 'image',
        'imgSize': 'large',
        'safe': 'active'
    }

    try:
        weather_data = requests.get(weather_url, params=weather_params).json()

        description = weather_data['weather'][0]['description']
        icon = weather_data['weather'][0]['icon']
        temp = weather_data['main']['temp']

        coord = weather_data['coord']
        wind = weather_data['wind']
        rain = weather_data.get('rain', {"1h": 0})
        clouds = weather_data['clouds']
        sys = weather_data['sys']

        day = dt.now().strftime('%d %B %Y')

        image_response = requests.get(search_url, params=search_params).json()
        search_items = image_response.get("items", [])

        if search_items:
            image_url = search_items[0]['link']
        else:
            image_url = None

        # Calculate wave properties
        temperature_celsius = temp
        wind_speed = wind['speed']

        g = 9.8
        T = 1 / np.sqrt(wind_speed)
        wavelength = (g * T**2) / (2 * np.pi)
        wave_depth = wavelength / (2 * np.pi)

        # Prepare data for plotting
        properties = ['Wind Speed (m/s)', 'Wave Period (s)', 'Wavelength (m)', 'Wave Depth (m)', 'Temperature (°C)']
        values = [wind_speed, T, wavelength, wave_depth, temperature_celsius]

        # Create modern line plot using Plotly
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=properties, y=values, mode='lines+markers',
                                 line=dict(color='blue', width=2),
                                 marker=dict(size=10, color='blue', symbol='circle')))
        fig.update_layout(
            title='Weather and Wave Properties',
            xaxis_title='Properties',
            yaxis_title='Values',
            template='plotly_white',
            font=dict(size=12),
            margin=dict(l=40, r=40, t=50, b=40)
        )

        # Convert plotly graph to HTML div string
        plot_html = fig.to_html(full_html=False, default_height=500)

        return render(request, 'Dashboard/weather3.html', {
            'description': description,
            'icon': icon,
            'temp': temp,
            'day': day,
            'city': city,
            'exception_occurred': False,
            'image_url': image_url,
            'plot_html': plot_html,

            # Additional weather data
            'coord_lat': coord['lat'],
            'coord_lon': coord['lon'],
            'weather_main': weather_data['weather'][0]['main'],
            'weather_description': weather_data['weather'][0]['description'],
            'feels_like': temperature_celsius,
            'temp_min': weather_data['main']['temp_min'],
            'temp_max': weather_data['main']['temp_max'],
            'pressure': weather_data['main']['pressure'],
            'humidity': weather_data['main']['humidity'],
            'wind_speed': wind_speed,
            'wind_deg': wind['deg'],
            'rain_1h': rain.get('1h', 0),
            'cloudiness': clouds['all'],
            'sunrise': dt.fromtimestamp(sys.get('sunrise', 0)).strftime('%H:%M:%S'),
            'sunset': dt.fromtimestamp(sys.get('sunset', 0)).strftime('%H:%M:%S'),
            'timezone': weather_data['timezone'],
            'country': sys['country'],
            'wave_period': T,
            'wavelength': wavelength,
            'wave_depth': wave_depth,
        })

    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        day = dt.now().strftime('%d %B %Y')
        return render(request, 'Dashboard/weather3.html', {
            'description': 'clear sky',
            'icon': '01d',
            'temp': 25,
            'day': day,
            'city': 'indore',
            'exception_occurred': True,
            'image_url': None,
            'plot_html': None,
        })
########################################################################################################
def adminlogout(request):
    if request.method == "POST":
        auth_logout(request)
        return JsonResponse({'success': True, 'message': 'Logout Successfully'})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=400)
######################################################################################################################
@csrf_exempt
def save_weather_condition(request):
    if request.method == 'POST':
        city = request.POST.get('city', '').strip()
        weather_condition = request.POST.get('weather_condition', '').strip()
        temperature = request.POST.get('temperature', '').strip()
        humidity = request.POST.get('humidity', '').strip()
        pressure = request.POST.get('pressure', '').strip()
        wind_speed = request.POST.get('wind_speed', '').strip()
        cloudiness = request.POST.get('cloudiness', '').strip()
        sunrise = request.POST.get('sunrise', '').strip()
        sunset = request.POST.get('sunset', '').strip()
        country = request.POST.get('country', '').strip()
        wave_period = request.POST.get('wave_period', '').strip()
        wavelength = request.POST.get('wavelength', '').strip()
        wave_depth = request.POST.get('wave_depth', '').strip()

        # Server-side validation for empty fields
        required_fields = [
            city, weather_condition, temperature, humidity, pressure,
            wind_speed, cloudiness, sunrise, sunset, country,
            wave_period, wavelength, wave_depth
        ]
        if not all(required_fields):
            return JsonResponse({'success': False, 'message': 'All fields are required'})

        try:
            # Check if a record with the same country already exists
            if CurrentWeatherCondition.objects.filter(country=country).exists():
                return JsonResponse({'success':False, 'message': 'this type Weather records is already saved'})

            # Save the weather record
            weather_record = CurrentWeatherCondition(
                location_city_name=city,
                weather_condition=weather_condition,
                weather_temperature=temperature,
                humidity=humidity,
                pressure=pressure,
                wind_speed=wind_speed,
                cloudiness=cloudiness,
                sunrise=sunrise,
                sunset=sunset,
                country=country,
                wave_period=wave_period,
                wavelength=wavelength,
                wave_depth=wave_depth
            )
            weather_record.save()
            return JsonResponse({'success': True, 'message': 'Weather record saved successfully'})

        except IntegrityError as e:
            return JsonResponse({'success': False, 'message': f'Error saving record: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})
##############################################################################################################
def Country4(request):
    # Get the city from the form, defaulting to 'Terengganu' if not provided
    city = request.POST.get('city', 'Terengganu')
    # OpenWeather API URL and parameters
    weather_url = 'https://api.openweathermap.org/data/2.5/weather'
    WEATHER_API_KEY = '39695639fa6ea8973a7ac6690056135b'
    weather_params = {'q': city, 'appid': WEATHER_API_KEY, 'units': 'metric'}
    # Google Custom Search API URL and parameters for landscape images
    SEARCH_ENGINE_ID = '040d46d9d92544fe7'
    API_KEY = 'AIzaSyDatm0RfUn7aVVKewPfSNXJXFa7qD84Shg'
    query = f"{city} landscape"
    page = 1
    start = (page - 1) * 10 + 1
    search_url = "https://www.googleapis.com/customsearch/v1"
    search_params = {
        'key': API_KEY,
        'cx': SEARCH_ENGINE_ID,
        'q': query,
        'start': start,
        'searchType': 'image',
        'imgSize': 'large',
        'safe': 'active'
    }
    try:
        # Fetch weather data
        weather_data = requests.get(weather_url, params=weather_params).json()
        description = weather_data['weather'][0]['description']
        icon = weather_data['weather'][0]['icon']
        temp = weather_data['main']['temp']
        coord = weather_data['coord']
        wind = weather_data['wind']
        rain = weather_data.get('rain', {"1h": 0})
        clouds = weather_data['clouds']
        sys = weather_data['sys']
        day = dt.now().strftime('%d %B %Y')
        # Fetch landscape image data
        image_response = requests.get(search_url, params=search_params).json()
        search_items = image_response.get("items", [])
        image_url = search_items[0]['link'] if search_items else None
        # Calculate wave properties
        temperature_celsius = temp
        wind_speed = wind['speed']
        g = 9.8
        T = 1 / np.sqrt(wind_speed)
        wavelength = (g * T**2) / (2 * np.pi)
        wave_depth = wavelength / (2 * np.pi)
        # Prepare data for plotting
        properties = ['Wind Speed (m/s)', 'Wave Period (s)', 'Wavelength (m)', 'Wave Depth (m)', 'Temperature (°C)']
        values = [wind_speed, T, wavelength, wave_depth, temperature_celsius]
        # Create plot using Plotly
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=properties, y=values, mode='lines+markers',
                                 line=dict(color='blue', width=2),
                                 marker=dict(size=10, color='blue', symbol='circle')))
        fig.update_layout(
            title='Weather and Wave Properties',
            xaxis_title='Properties',
            yaxis_title='Values',
            template='plotly_white',
            font=dict(size=12),
            margin=dict(l=40, r=40, t=50, b=40)
        )
        # Convert plotly graph to HTML div string
        plot_html = fig.to_html(full_html=False, default_height=500)
        return render(request, 'Dashboard/current_weather.html', {
            'description': description,
            'icon': icon,
            'temp': temp,
            'day': day,
            'city': city,
            'exception_occurred': False,
            'image_url': image_url,
            'plot_html': plot_html,
            # Additional weather data
            'coord_lat': coord['lat'],
            'coord_lon': coord['lon'],
            'weather_main': weather_data['weather'][0]['main'],
            'weather_description': description,
            'feels_like': temperature_celsius,
            'temp_min': weather_data['main']['temp_min'],
            'temp_max': weather_data['main']['temp_max'],
            'pressure': weather_data['main']['pressure'],
            'humidity': weather_data['main']['humidity'],
            'wind_speed': wind_speed,
            'wind_deg': wind['deg'],
            'rain_1h': rain.get('1h', 0),
            'cloudiness': clouds['all'],
            'sunrise': dt.fromtimestamp(sys.get('sunrise', 0)).strftime('%H:%M:%S'),
            'sunset': dt.fromtimestamp(sys.get('sunset', 0)).strftime('%H:%M:%S'),
            'timezone': weather_data['timezone'],
            'country': sys['country'],
            'wave_period': T,
            'wavelength': wavelength,
            'wave_depth': wave_depth,
        })

    except Exception as e:
        # Handle errors gracefully
        messages.error(request, f'An error occurred: {str(e)}')
        day = dt.now().strftime('%d %B %Y')
        return render(request, 'Dashboard/current_weather.html', {
            'description': 'clear sky',
            'icon': '01d',
            'temp': 25,
            'day': day,
            'city': 'Terengganu',
            'exception_occurred': True,
            'image_url': None,
            'plot_html': None,
        })  
#########################################################
def View_all_current(request):
    weather_records = CurrentWeatherCondition.objects.all()
    return render(request, 'Dashboard/view_current.html', {'weather_records': weather_records})
################################################################################################################
def Country5(request):
    city = request.POST.get('city', 'Balau')

    weather_url = f'https://api.openweathermap.org/data/2.5/weather'
    WEATHER_API_KEY = '39695639fa6ea8973a7ac6690056135b'
    weather_params = {'q': city, 'appid': WEATHER_API_KEY, 'units': 'metric'}

    SEARCH_ENGINE_ID = '040d46d9d92544fe7'
    API_KEY = 'AIzaSyDatm0RfUn7aVVKewPfSNXJXFa7qD84Shg'
    query = city + " landscape"
    page = 1
    start = (page - 1) * 10 + 1
    search_url = f"https://www.googleapis.com/customsearch/v1"
    search_params = {
        'key': API_KEY,
        'cx': SEARCH_ENGINE_ID,
        'q': query,
        'start': start,
        'searchType': 'image',
        'imgSize': 'large',
        'safe': 'active'
    }

    try:
        weather_data = requests.get(weather_url, params=weather_params).json()

        description = weather_data['weather'][0]['description']
        icon = weather_data['weather'][0]['icon']
        temp = weather_data['main']['temp']

        coord = weather_data['coord']
        wind = weather_data['wind']
        rain = weather_data.get('rain', {"1h": 0})
        clouds = weather_data['clouds']
        sys = weather_data['sys']

        day = dt.now().strftime('%d %B %Y')

        image_response = requests.get(search_url, params=search_params).json()
        search_items = image_response.get("items", [])

        if search_items:
            image_url = search_items[0]['link']
        else:
            image_url = None

        # Calculate wave properties
        temperature_celsius = temp
        wind_speed = wind['speed']

        g = 9.8
        T = 1 / np.sqrt(wind_speed)
        wavelength = (g * T**2) / (2 * np.pi)
        wave_depth = wavelength / (2 * np.pi)

        # Prepare data for plotting
        properties = ['Wind Speed (m/s)', 'Wave Period (s)', 'Wavelength (m)', 'Wave Depth (m)', 'Temperature (°C)']
        values = [wind_speed, T, wavelength, wave_depth, temperature_celsius]

        # Create modern line plot using Plotly
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=properties, y=values, mode='lines+markers',
                                 line=dict(color='blue', width=2),
                                 marker=dict(size=10, color='blue', symbol='circle')))
        fig.update_layout(
            title='Weather and Wave Properties',
            xaxis_title='Properties',
            yaxis_title='Values',
            template='plotly_white',
            font=dict(size=12),
            margin=dict(l=40, r=40, t=50, b=40)
        )

        # Convert plotly graph to HTML div string
        plot_html = fig.to_html(full_html=False, default_height=500)

        return render(request, 'Dashboard/weather4.html', {
            'description': description,
            'icon': icon,
            'temp': temp,
            'day': day,
            'city': city,
            'exception_occurred': False,
            'image_url': image_url,
            'plot_html': plot_html,

            # Additional weather data
            'coord_lat': coord['lat'],
            'coord_lon': coord['lon'],
            'weather_main': weather_data['weather'][0]['main'],
            'weather_description': weather_data['weather'][0]['description'],
            'feels_like': temperature_celsius,
            'temp_min': weather_data['main']['temp_min'],
            'temp_max': weather_data['main']['temp_max'],
            'pressure': weather_data['main']['pressure'],
            'humidity': weather_data['main']['humidity'],
            'wind_speed': wind_speed,
            'wind_deg': wind['deg'],
            'rain_1h': rain.get('1h', 0),
            'cloudiness': clouds['all'],
            'sunrise': dt.fromtimestamp(sys.get('sunrise', 0)).strftime('%H:%M:%S'),
            'sunset': dt.fromtimestamp(sys.get('sunset', 0)).strftime('%H:%M:%S'),
            'timezone': weather_data['timezone'],
            'country': sys['country'],
            'wave_period': T,
            'wavelength': wavelength,
            'wave_depth': wave_depth,
        })

    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        day = dt.now().strftime('%d %B %Y')
        return render(request, 'Dashboard/weather4.html', {
            'description': 'clear sky',
            'icon': '01d',
            'temp': 25,
            'day': day,
            'city': 'indore',
            'exception_occurred': True,
            'image_url': None,
            'plot_html': None,
        })
################################################################################################################
def Country6(request):
    city = request.POST.get('city', 'Beach')

    weather_url = f'https://api.openweathermap.org/data/2.5/weather'
    WEATHER_API_KEY = '39695639fa6ea8973a7ac6690056135b'
    weather_params = {'q': city, 'appid': WEATHER_API_KEY, 'units': 'metric'}

    SEARCH_ENGINE_ID = '040d46d9d92544fe7'
    API_KEY = 'AIzaSyDatm0RfUn7aVVKewPfSNXJXFa7qD84Shg'
    query = city + " landscape"
    page = 1
    start = (page - 1) * 10 + 1
    search_url = f"https://www.googleapis.com/customsearch/v1"
    search_params = {
        'key': API_KEY,
        'cx': SEARCH_ENGINE_ID,
        'q': query,
        'start': start,
        'searchType': 'image',
        'imgSize': 'large',
        'safe': 'active'
    }

    try:
        weather_data = requests.get(weather_url, params=weather_params).json()

        description = weather_data['weather'][0]['description']
        icon = weather_data['weather'][0]['icon']
        temp = weather_data['main']['temp']

        coord = weather_data['coord']
        wind = weather_data['wind']
        rain = weather_data.get('rain', {"1h": 0})
        clouds = weather_data['clouds']
        sys = weather_data['sys']

        day = dt.now().strftime('%d %B %Y')

        image_response = requests.get(search_url, params=search_params).json()
        search_items = image_response.get("items", [])

        if search_items:
            image_url = search_items[0]['link']
        else:
            image_url = None

        # Calculate wave properties
        temperature_celsius = temp
        wind_speed = wind['speed']

        g = 9.8
        T = 1 / np.sqrt(wind_speed)
        wavelength = (g * T**2) / (2 * np.pi)
        wave_depth = wavelength / (2 * np.pi)

        # Prepare data for plotting
        properties = ['Wind Speed (m/s)', 'Wave Period (s)', 'Wavelength (m)', 'Wave Depth (m)', 'Temperature (°C)']
        values = [wind_speed, T, wavelength, wave_depth, temperature_celsius]

        # Create modern line plot using Plotly
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=properties, y=values, mode='lines+markers',
                                 line=dict(color='blue', width=2),
                                 marker=dict(size=10, color='blue', symbol='circle')))
        fig.update_layout(
            title='Weather and Wave Properties',
            xaxis_title='Properties',
            yaxis_title='Values',
            template='plotly_white',
            font=dict(size=12),
            margin=dict(l=40, r=40, t=50, b=40)
        )

        # Convert plotly graph to HTML div string
        plot_html = fig.to_html(full_html=False, default_height=500)

        return render(request, 'Dashboard/weather5.html', {
            'description': description,
            'icon': icon,
            'temp': temp,
            'day': day,
            'city': city,
            'exception_occurred': False,
            'image_url': image_url,
            'plot_html': plot_html,

            # Additional weather data
            'coord_lat': coord['lat'],
            'coord_lon': coord['lon'],
            'weather_main': weather_data['weather'][0]['main'],
            'weather_description': weather_data['weather'][0]['description'],
            'feels_like': temperature_celsius,
            'temp_min': weather_data['main']['temp_min'],
            'temp_max': weather_data['main']['temp_max'],
            'pressure': weather_data['main']['pressure'],
            'humidity': weather_data['main']['humidity'],
            'wind_speed': wind_speed,
            'wind_deg': wind['deg'],
            'rain_1h': rain.get('1h', 0),
            'cloudiness': clouds['all'],
            'sunrise': dt.fromtimestamp(sys.get('sunrise', 0)).strftime('%H:%M:%S'),
            'sunset': dt.fromtimestamp(sys.get('sunset', 0)).strftime('%H:%M:%S'),
            'timezone': weather_data['timezone'],
            'country': sys['country'],
            'wave_period': T,
            'wavelength': wavelength,
            'wave_depth': wave_depth,
        })

    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        day = dt.now().strftime('%d %B %Y')
        return render(request, 'Dashboard/weather5.html', {
            'description': 'clear sky',
            'icon': '01d',
            'temp': 25,
            'day': day,
            'city': 'indore',
            'exception_occurred': True,
            'image_url': None,
            'plot_html': None,
        })
###########################################################################################################################################################
def Country7(request):
    city = request.POST.get('city', 'Pulau')

    weather_url = f'https://api.openweathermap.org/data/2.5/weather'
    WEATHER_API_KEY = '39695639fa6ea8973a7ac6690056135b'
    weather_params = {'q': city, 'appid': WEATHER_API_KEY, 'units': 'metric'}

    SEARCH_ENGINE_ID = '040d46d9d92544fe7'
    API_KEY = 'AIzaSyDatm0RfUn7aVVKewPfSNXJXFa7qD84Shg'
    query = city + " landscape"
    page = 1
    start = (page - 1) * 10 + 1
    search_url = f"https://www.googleapis.com/customsearch/v1"
    search_params = {
        'key': API_KEY,
        'cx': SEARCH_ENGINE_ID,
        'q': query,
        'start': start,
        'searchType': 'image',
        'imgSize': 'large',
        'safe': 'active'
    }

    try:
        weather_data = requests.get(weather_url, params=weather_params).json()

        description = weather_data['weather'][0]['description']
        icon = weather_data['weather'][0]['icon']
        temp = weather_data['main']['temp']

        coord = weather_data['coord']
        wind = weather_data['wind']
        rain = weather_data.get('rain', {"1h": 0})
        clouds = weather_data['clouds']
        sys = weather_data['sys']

        day = dt.now().strftime('%d %B %Y')

        image_response = requests.get(search_url, params=search_params).json()
        search_items = image_response.get("items", [])

        if search_items:
            image_url = search_items[0]['link']
        else:
            image_url = None

        # Calculate wave properties
        temperature_celsius = temp
        wind_speed = wind['speed']

        g = 9.8
        T = 1 / np.sqrt(wind_speed)
        wavelength = (g * T**2) / (2 * np.pi)
        wave_depth = wavelength / (2 * np.pi)

        # Prepare data for plotting
        properties = ['Wind Speed (m/s)', 'Wave Period (s)', 'Wavelength (m)', 'Wave Depth (m)', 'Temperature (°C)']
        values = [wind_speed, T, wavelength, wave_depth, temperature_celsius]

        # Create modern line plot using Plotly
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=properties, y=values, mode='lines+markers',
                                 line=dict(color='blue', width=2),
                                 marker=dict(size=10, color='blue', symbol='circle')))
        fig.update_layout(
            title='Weather and Wave Properties',
            xaxis_title='Properties',
            yaxis_title='Values',
            template='plotly_white',
            font=dict(size=12),
            margin=dict(l=40, r=40, t=50, b=40)
        )

        # Convert plotly graph to HTML div string
        plot_html = fig.to_html(full_html=False, default_height=500)

        return render(request, 'Dashboard/weather6.html', {
            'description': description,
            'icon': icon,
            'temp': temp,
            'day': day,
            'city': city,
            'exception_occurred': False,
            'image_url': image_url,
            'plot_html': plot_html,

            # Additional weather data
            'coord_lat': coord['lat'],
            'coord_lon': coord['lon'],
            'weather_main': weather_data['weather'][0]['main'],
            'weather_description': weather_data['weather'][0]['description'],
            'feels_like': temperature_celsius,
            'temp_min': weather_data['main']['temp_min'],
            'temp_max': weather_data['main']['temp_max'],
            'pressure': weather_data['main']['pressure'],
            'humidity': weather_data['main']['humidity'],
            'wind_speed': wind_speed,
            'wind_deg': wind['deg'],
            'rain_1h': rain.get('1h', 0),
            'cloudiness': clouds['all'],
            'sunrise': dt.fromtimestamp(sys.get('sunrise', 0)).strftime('%H:%M:%S'),
            'sunset': dt.fromtimestamp(sys.get('sunset', 0)).strftime('%H:%M:%S'),
            'timezone': weather_data['timezone'],
            'country': sys['country'],
            'wave_period': T,
            'wavelength': wavelength,
            'wave_depth': wave_depth,
        })

    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        day = dt.now().strftime('%d %B %Y')
        return render(request, 'Dashboard/weather6.html', {
            'description': 'clear sky',
            'icon': '01d',
            'temp': 25,
            'day': day,
            'city': 'indore',
            'exception_occurred': True,
            'image_url': None,
            'plot_html': None,
        })
###################################################################################################################################################
##########(#############################(every days provide upcomming 16days prediction)###############################################)
#########################################################################################
g=9.8  # Acceleration due to gravity (m/s²)
API_KEY = '39695639fa6ea8973a7ac6690056135b'
def generate_weather_wave_data(city_name):
    try:
        # Fetch geocoding data
        geocoding_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit=1&appid={API_KEY}"
        response = requests.get(geocoding_url)
        response.raise_for_status()
        geocoding_data = response.json()

        if len(geocoding_data) == 0:
            return None, "City not found!"

        lat = geocoding_data[0]['lat']
        lon = geocoding_data[0]['lon']

        # Fetch weather forecast data (16 days prediction)
        weather_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        response = requests.get(weather_url)
        response.raise_for_status()
        weather_data = response.json()

        # Prepare data for storage and plotting
        daily_data = []
        for record in weather_data['list']:
            date_time = record['dt_txt']
            date = date_time.split(' ')[0]
            temp = record['main']['temp']
            feels_like = record['main']['feels_like']
            temp_min = record['main']['temp_min']
            temp_max = record['main']['temp_max']
            pressure = record['main']['pressure']
            humidity = record['main']['humidity']
            wind_speed = record['wind']['speed']
            wind_direction = record['wind']['deg']
            weather_main = record['weather'][0]['main']
            weather_desc = record['weather'][0]['description']
            clouds = record['clouds']['all']
            rain = record.get('rain', {}).get('3h', 0)  # Rain in the last 3 hours

            # Wave calculations
            T = 1 / np.sqrt(wind_speed) if wind_speed > 0 else 0  # Wave period (s)
            wavelength = (g * T**2) / (2 * np.pi) if T > 0 else 0  # Wavelength (m)
            wave_depth = wavelength / (2 * np.pi) if wavelength > 0 else 0  # Wave depth (m)

            # Additional weather details
            coord_lat = lat
            coord_lon = lon
            sunrise = dt.fromtimestamp(record['dt'] - weather_data['city']['timezone']).strftime('%H:%M:%S')
            sunset = dt.fromtimestamp(record['dt'] + weather_data['city']['timezone']).strftime('%H:%M:%S')
            country = weather_data['city']['country']

            # Store data with updated keys
            daily_data.append({
                'description': weather_desc,
                'icon': record['weather'][0]['icon'],
                'temp': temp,
                'day': date,
                'city': city_name,
                'exception_occurred': False,  # You can adjust this based on your needs
                'image_url': f"http://openweathermap.org/img/wn/{record['weather'][0]['icon']}@2x.png",  # Icon URL

                # Additional weather data
                'coord_lat': coord_lat,
                'coord_lon': coord_lon,
                'weather_main': weather_main,
                'weather_description': weather_desc,
                'feels_like': feels_like,
                'temp_min': temp_min,
                'temp_max': temp_max,
                'pressure': pressure,
                'humidity': humidity,
                'wind_speed': wind_speed,
                'wind_deg': wind_direction,
                'rain_1h': rain,
                'cloudiness': clouds,
                'sunrise': sunrise,
                'sunset': sunset,
                'timezone': weather_data['city']['timezone'],
                'country': country,
                'wave_period': T,
                'wavelength': wavelength,
                'wave_depth': wave_depth,
            })

        # Convert to DataFrame for easier handling
        df = pd.DataFrame(daily_data)

        # Save data to CSV
        df.to_csv("weather_wave_data_16days.csv", index=False)

        # Generate daily graphs using Plotly
        for date in df["day"].unique():
            day_data = df[df["day"] == date]

            # Melt the data to long format for plotting
            melted_data = pd.melt(day_data, id_vars=["day"], value_vars=["temp", "feels_like", "wind_speed", "wave_period", "wavelength", "wave_depth"],
                                  var_name="Metrics", value_name="Average Value")

            fig = px.bar(melted_data, x="Metrics", y="Average Value", 
                         title=f"Weather and Wave Metrics for {date}",
                         labels={'Average Value': 'Average Value', 'Metrics': 'Metrics'},
                         template="plotly_dark")

            fig.write_image(f"{date}_daily_graph.png")  # Save each day's graph

        # Melt the data to long format for plotting
        melted_data = pd.melt(df, id_vars=["day"], value_vars=["temp", "feels_like", "wind_speed", "wave_period", "wavelength", "wave_depth"],
                            var_name="Metrics", value_name="Average Value")

        # Generate a combined graph for all 16 days
        fig = px.line(melted_data, x="day", y="Average Value", color="Metrics",
                    title="16-Day Trend of Weather and Wave Metrics",
                    labels={"Average Value": "Metrics Value", "day": "Date", "Metrics": "Metric"},
                    template="plotly_dark")

        # Customize the layout for better readability
        fig.update_layout(title_font_size=24)

        # Save the combined graph as an image
        fig.write_image("16_days_combined_graph.png")  # Save combined graph


        return df, None

    except requests.exceptions.RequestException as e:
        return None, str(e)
    except Exception as e:
        return None, str(e)
############################################################################
def weather_forecast_view(request):
    city_name = "Terengganu"  # Set the default city name

    if request.method == "POST":
        city_name = request.POST.get("city_name")  # Get city name from the form (if provided)
        
    data, error = generate_weather_wave_data(city_name)

    if error:
        return render(request, "Dashboard/future.html", {"error": error})

    records = data.to_dict(orient="records")  # Convert DataFrame to a list of dictionaries
    
    # Move the generated images to static folder
    for date in data["day"].unique():
        fig_path = f"{date}_daily_graph.png"
        shutil.move(fig_path, f"static/{fig_path}")  # Update the path if needed
    
    combined_graph_path = "16_days_combined_graph.png"
    shutil.move(combined_graph_path, f"static/{combined_graph_path}")  # Move the combined graph

    # Pass the full data to the template
    return render(request, "Dashboard/future.html", {"records": records})
####################################################################################################
############################################################################
def weather_forecast_view1(request):
    city_name = "Terengganu"  # Set the default city name
    if request.method == "POST":
        city_name = request.POST.get("city_name")  # Get city name from the form (if provided)
    data, error = generate_weather_wave_data(city_name)
    
    if error:
        return render(request, "Dashboard/all_future.html", {"error": error})
    
    records = data.to_dict(orient="records")  # Convert DataFrame to a list of dictionaries

    # Save records into the database, preventing duplicates
    for index, record in data.iterrows():
        # Check if a record already exists for the same city and date (or other unique fields)
        if not FutureWeather16dayspredictionModel.objects.filter(city_name=record['city'], sunrise=record['sunrise']).exists():
            try:
                FutureWeather16dayspredictionModel.objects.create(
                    city_name=record['city'],
                    description=record['description'],
                    weather_main=record['weather_main'],
                    weather_description=record['weather_description'],
                    temp=record['temp'],
                    feels_like=record['feels_like'],
                    temp_min=record['temp_min'],
                    temp_max=record['temp_max'],
                    pressure=record['pressure'],
                    humidity=record['humidity'],
                    wind_speed=record['wind_speed'],
                    wind_deg=record['wind_deg'],
                    rain_1h=record['rain_1h'],
                    cloudiness=record['cloudiness'],
                    sunrise=record['sunrise'],
                    sunset=record['sunset'],
                    timezone=record['timezone'],
                    country=record['country'],
                    wave_period=record['wave_period'],
                    wavelength=record['wavelength'],
                    wave_depth=record['wave_depth']
                )
            except IntegrityError:
                continue  # Skip any record that causes a duplicate entry error

    # Move the generated images to the static folder
    for date in data["day"].unique():
        fig_path = f"{date}_daily_graph.png"
        shutil.move(fig_path, f"static/Future_data/{fig_path}")  # Update the path if needed
    
    combined_graph_path = "16_days_combined_graph.png"
    shutil.move(combined_graph_path, f"static/Future_data/{combined_graph_path}")  # Move the combined graph

    # Pass the full data to the template
    return render(request, "Dashboard/all_future.html", {"records": records, "success": "Records saved successfully!"})
################################################################################################
def My_Future(request):
    # Get the count of current weather records
    total_future_weather_count=FutureWeather16dayspredictionModel.objects.all()
    return render(request, 'Dashboard/view_future.html', {'total_future_weather_count':total_future_weather_count})

