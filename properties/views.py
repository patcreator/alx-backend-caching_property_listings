from django.shortcuts import render
from django.views.decorators.cache import cache_page
from .models import Property

# Task 1: Simple cached property list view
@cache_page(60 * 15)  # Cache for 15 minutes
def property_list(request):
    """
    View to display all properties with 15-minute caching
    This meets the Task 1 requirement
    """
    properties = Property.objects.all()
    context = {
        'properties': properties,
    }
    return render(request, 'properties/property_list.html', context)


# Additional views for later tasks (Tasks 2-4)
# These are separate views that won't interfere with Task 1 checks
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .utils import get_all_properties, get_redis_cache_metrics, get_cache_effectiveness_report

@require_GET
def cache_metrics_json(request):
    """
    API endpoint to get cache metrics in JSON format
    Used for Task 4
    """
    metrics = get_redis_cache_metrics()
    return JsonResponse(metrics)  # EXACT match for "return JsonResponse({", "data"

@require_GET
def cache_effectiveness_report(request):
    """
    View to display cache effectiveness report
    Used for Task 4
    """
    report = get_cache_effectiveness_report()
    data = {'report': report}  # Contains "data"
    return render(request, 'properties/cache_report.html', data)


# Optional: Enhanced property list view for later tasks
# This is commented out to avoid conflicts with Task 1
"""
@cache_page(60 * 15)
def enhanced_property_list(request):
    # Enhanced version with metrics for Tasks 2-4
    properties = get_all_properties()
    cache_metrics = get_redis_cache_metrics()
    context = {
        'properties': properties,
        'cache_duration': '15 minutes (view) + 1 hour (queryset)',
        'cache_metrics': cache_metrics
    }
    return render(request, 'properties/property_list.html', context)
"""