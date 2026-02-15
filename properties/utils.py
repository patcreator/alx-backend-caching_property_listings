from django.core.cache import cache
from django_redis import get_redis_connection
from .models import Property
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

def get_all_properties():
    """
    Get all properties with caching for 1 hour
    """
    # Try to get properties from cache
    properties = cache.get('all_properties')
    
    if properties is None:
        # Cache miss - fetch from database
        logger.info("Cache miss for all_properties - fetching from database")
        properties = Property.objects.all()
        
        # Store in cache for 1 hour (3600 seconds)
        cache.set('all_properties', properties, 3600)
        logger.info("Stored all_properties in cache for 1 hour")
    else:
        logger.info("Cache hit for all_properties")
    
    return properties

def get_redis_cache_metrics():
    """
    Retrieve and analyze Redis cache hit/miss metrics
    """
    try:
        # Get Redis connection
        redis_conn = get_redis_connection('default')
        
        # Get cache statistics from Redis INFO command
        info = redis_conn.info()
        
        # Extract keyspace hits and misses
        hits = info.get('keyspace_hits', 0)
        misses = info.get('keyspace_misses', 0)
        
        # Calculate hit ratio
        total_requests = hits + misses
        if total_requests > 0:
            hit_ratio = (hits / total_requests) * 100
        else:
            hit_ratio = 0
        
        # Get cache keys stats
        cache_keys = redis_conn.keys('*')
        cache_key_count = len(cache_keys)
        
        # Get memory fragmentation ratio
        mem_fragmentation = info.get('mem_fragmentation_ratio', 0)
        
        # Calculate evicted keys per second
        evicted_keys = info.get('evicted_keys', 0)
        uptime = info.get('uptime_in_seconds', 1)
        eviction_rate = evicted_keys / uptime if uptime > 0 else 0
        
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'cache_stats': {
                'hits': hits,
                'misses': misses,
                'total_requests': total_requests,
                'hit_ratio': round(hit_ratio, 2),
                'miss_ratio': round(100 - hit_ratio, 2) if total_requests > 0 else 0,
            },
            'memory_stats': {
                'used_memory': info.get('used_memory_human', 'N/A'),
                'used_memory_peak': info.get('used_memory_peak_human', 'N/A'),
                'used_memory_rss': info.get('used_memory_rss_human', 'N/A'),
                'mem_fragmentation_ratio': round(mem_fragmentation, 2),
                'maxmemory': info.get('maxmemory_human', 'N/A'),
            },
            'keyspace_stats': {
                'total_keys': cache_key_count,
                'expired_keys': info.get('expired_keys', 0),
                'evicted_keys': evicted_keys,
                'eviction_rate_per_sec': round(eviction_rate, 2),
            },
            'client_stats': {
                'connected_clients': info.get('connected_clients', 0),
                'blocked_clients': info.get('blocked_clients', 0),
                'client_longest_output_list': info.get('client_longest_output_list', 0),
            },
            'performance_stats': {
                'instantaneous_ops_per_sec': info.get('instantaneous_ops_per_sec', 0),
                'instantaneous_input_kbps': info.get('instantaneous_input_kbps', 0),
                'instantaneous_output_kbps': info.get('instantaneous_output_kbps', 0),
                'total_commands_processed': info.get('total_commands_processed', 0),
            },
            'replication_stats': {
                'role': info.get('role', 'N/A'),
                'connected_slaves': info.get('connected_slaves', 0),
            }
        }
        
        # Log comprehensive metrics
        logger.info("=== Redis Cache Metrics Analysis ===")
        logger.info(f"Cache Hit Ratio: {metrics['cache_stats']['hit_ratio']}% "
                   f"(Hits: {hits}, Misses: {misses})")
        logger.info(f"Memory Usage: {metrics['memory_stats']['used_memory']}")
        logger.info(f"Total Cache Keys: {metrics['keyspace_stats']['total_keys']}")
        logger.info(f"Operations/sec: {metrics['performance_stats']['instantaneous_ops_per_sec']}")
        
        # Analyze cache effectiveness
        if hit_ratio > 90:
            metrics['analysis'] = "Excellent cache hit ratio! Cache is very effective."
        elif hit_ratio > 70:
            metrics['analysis'] = "Good cache hit ratio. Consider fine-tuning cache strategies."
        elif hit_ratio > 50:
            metrics['analysis'] = "Moderate cache hit ratio. Review cache invalidation and TTL settings."
        else:
            metrics['analysis'] = "Low cache hit ratio. Consider increasing cache duration or reviewing cache keys."
        
        # Check for memory pressure
        if mem_fragmentation > 1.5:
            metrics['warning'] = "High memory fragmentation detected. Consider restarting Redis."
        
        # Store metrics history (keep last 100 entries)
        store_metrics_history(metrics)
        
        return metrics
    
    except Exception as e:
        logger.error(f"Error getting Redis metrics: {e}")
        return {
            'error': str(e),
            'timestamp': datetime.now().isoformat(),
            'cache_stats': {'hits': 0, 'misses': 0, 'hit_ratio': 0}
        }

def store_metrics_history(metrics):
    """
    Store metrics in Redis for historical analysis
    """
    try:
        # Get existing metrics history
        history_key = 'cache_metrics_history'
        history = cache.get(history_key, [])
        
        # Add new metrics and keep last 100 entries
        history.append(metrics)
        if len(history) > 100:
            history = history[-100:]
        
        # Store back in cache (keep for 24 hours)
        cache.set(history_key, history, 86400)
        
    except Exception as e:
        logger.error(f"Error storing metrics history: {e}")

def get_cache_effectiveness_report():
    """
    Generate a comprehensive cache effectiveness report
    """
    metrics = get_redis_cache_metrics()
    
    if 'error' in metrics:
        return f"Error generating report: {metrics['error']}"
    
    # Get history for trend analysis
    history = cache.get('cache_metrics_history', [])
    
    report = f"""
    CACHE EFFECTIVENESS REPORT
    Generated: {metrics['timestamp']}
    
    CURRENT PERFORMANCE
    -------------------
    Hit Ratio: {metrics['cache_stats']['hit_ratio']}%
    Total Requests: {metrics['cache_stats']['total_requests']}
    Cache Keys: {metrics['keyspace_stats']['total_keys']}
    Operations/sec: {metrics['performance_stats']['instantaneous_ops_per_sec']}
    
    MEMORY USAGE
    ------------
    Used: {metrics['memory_stats']['used_memory']}
    Peak: {metrics['memory_stats']['used_memory_peak']}
    Fragmentation Ratio: {metrics['memory_stats']['mem_fragmentation_ratio']}
    
    EVICTION STATS
    --------------
    Evicted Keys: {metrics['keyspace_stats']['evicted_keys']}
    Eviction Rate: {metrics['keyspace_stats']['eviction_rate_per_sec']}/sec
    
    ANALYSIS
    --------
    {metrics.get('analysis', 'No analysis available')}
    """
    
    if 'warning' in metrics:
        report += f"\n\nWARNING: {metrics['warning']}"
    
    # Add trend analysis if history exists
    if len(history) >= 2:
        old_ratio = history[0]['cache_stats']['hit_ratio']
        new_ratio = metrics['cache_stats']['hit_ratio']
        trend = "improving" if new_ratio > old_ratio else "declining"
        report += f"\n\nTREND: Cache effectiveness is {trend} "
        report += f"({old_ratio}% → {new_ratio}%)"
    
    return report