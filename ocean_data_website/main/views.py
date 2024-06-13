from django.shortcuts import render
from django.http import JsonResponse
from .models import OceanData
import logging
from django.db.models import Min, Max

logger = logging.getLogger(__name__)

def index(request):
    return render(request, 'main/index.html')

def check_data_availability(request):
    source = request.GET.get('source')
    latitude = request.GET.get('latitude')
    longitude = request.GET.get('longitude')
    time = request.GET.get('time')

    filters = {'source': source}
    if latitude:
        filters['latitude'] = float(latitude)
    if longitude:
        filters['longitude'] = float(longitude)
    if time:
        filters['time'] = time

    exists = OceanData.objects.filter(**filters).exists()
    return JsonResponse({'exists': exists})

def get_data(request):
    source = request.GET.get('source')
    parameters = request.GET.getlist('parameters')
    north = float(request.GET.get('north'))
    south = float(request.GET.get('south'))
    east = float(request.GET.get('east'))
    west = float(request.GET.get('west'))
    start_time = request.GET.get('start_time')
    end_time = request.GET.get('end_time')

    filters = {
        'source': source,
        'latitude__lte': north,
        'latitude__gte': south,
        'longitude__lte': east,
        'longitude__gte': west,
        'time__range': [start_time, end_time]
    }

    values_list = ['latitude', 'longitude', 'time', 'depth']
    if 'temperature' in parameters:
        values_list.append('temperature')
    if 'salinity' in parameters:
        values_list.append('salinity')

    data = OceanData.objects.filter(**filters).values(*values_list)
    return JsonResponse(list(data), safe=False)
from django.db.models import Min, Max
from django.http import JsonResponse
from .models import OceanData

def get_available_data_ranges(request):
    source = request.GET.get('source')
    filters = {'source': source}

    # Check if data source is available
    if not OceanData.objects.filter(**filters).exists():
        return JsonResponse({
            'parameters': 'None',
            'latitude': '',
            'longitude': '',
            'time': ''
        })

    # Get available parameters
    available_parameters = []
    if OceanData.objects.filter(**filters, temperature__isnull=False).exists():
        available_parameters.append('Temperature')
    if OceanData.objects.filter(**filters, salinity__isnull=False).exists():
        available_parameters.append('Salinity')

    # Get available latitude and longitude ranges
    latitude_range = OceanData.objects.filter(**filters).aggregate(min_lat=Min('latitude'), max_lat=Max('latitude'))
    longitude_range = OceanData.objects.filter(**filters).aggregate(min_lon=Min('longitude'), max_lon=Max('longitude'))

    # Get available time range
    time_range = OceanData.objects.filter(**filters).aggregate(min_time=Min('time'), max_time=Max('time'))

    return JsonResponse({
        'parameters': ', '.join(available_parameters) or 'None',
        'latitude': f"{latitude_range['min_lat']} to {latitude_range['max_lat']}" if latitude_range['min_lat'] is not None else 'None',
        'longitude': f"{longitude_range['min_lon']} to {longitude_range['max_lon']}" if longitude_range['min_lon'] is not None else 'None',
        'time': f"{time_range['min_time']} to {time_range['max_time']}" if time_range['min_time'] is not None else 'None'
    })
