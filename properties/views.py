from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_GET
from .utils import get_all_properties, get_redis_cache_metrics, get_cache_effectiveness_report
import json

@cache_page(60 * 15)  # Cache for 15 minutes
def property_list(request):
    """
    View to display all properties using cached queryset
    """
    # Get properties using low-level caching
    properties = get_all_properties()
    
    # Get cache metrics for display
    cache_metrics = get_redis_cache_metrics()
    
    context = {
        'properties': properties,
        'cache_duration': '15 minutes (view) + 1 hour (queryset)',
        'cache_metrics': cache_metrics
    }
    return render(request, 'properties/property_list.html', context)

@require_GET
def cache_metrics_json(request):
    """
    API endpoint to get cache metrics in JSON format
    """
    metrics = get_redis_cache_metrics()
    return JsonResponse(metrics)

@require_GET
def cache_effectiveness_report(request):
    """
    View to display cache effectiveness report
    """
    report = get_cache_effectiveness_report()
    return render(request, 'properties/cache_report.html', {'report': report})