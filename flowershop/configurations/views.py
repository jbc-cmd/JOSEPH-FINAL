# Configurations views
from django.shortcuts import render


def get_service_config(service_name):
    """
    Retrieve service configuration from database.
    Safe way to get API credentials without storing in code.
    """
    from .models import ServiceConfig
    try:
        config = ServiceConfig.objects.get(
            service_name=service_name,
            is_active=True
        )
        return {
            'api_key': config.api_key,
            'api_secret': config.api_secret,
            'environment': config.environment
        }
    except ServiceConfig.DoesNotExist:
        return None


def get_general_config():
    """Get general shop configuration"""
    from .models import GeneralConfig
    try:
        return GeneralConfig.objects.first()
    except:
        return None
