from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Property
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Property)
def invalidate_property_cache_on_save(sender, instance, **kwargs):
    """
    Invalidate cache when a Property is created or updated
    """
    logger.info(f"Property {instance.id} saved - invalidating cache")
    cache.delete('all_properties')
    
    # Also delete any other related cache keys
    cache.delete_pattern('views.decorators.cache.*')  # Invalidate view caches

@receiver(post_delete, sender=Property)
def invalidate_property_cache_on_delete(sender, instance, **kwargs):
    """
    Invalidate cache when a Property is deleted
    """
    logger.info(f"Property {instance.id} deleted - invalidating cache")
    cache.delete('all_properties')
    cache.delete_pattern('views.decorators.cache.*')  # Invalidate view caches