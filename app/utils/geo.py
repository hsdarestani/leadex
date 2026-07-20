"""
Geolocation utility using GeoIP2
"""
import geoip2.database
import geoip2.errors
from typing import Optional, Dict
from app.core.config import settings
import os


def get_geo_info(ip_address: str) -> Optional[Dict[str, any]]:
    """
    Get geolocation information from IP address
    
    Args:
        ip_address: Client IP address
    
    Returns:
        Dictionary with geo info or None if lookup fails
    """
    # Skip private/local IPs
    if ip_address in ["127.0.0.1", "localhost", "::1"]:
        return {
            "country": "LOCAL",
            "city": "Local",
            "lat": 0.0,
            "lon": 0.0
        }
    
    # Check if GeoIP database exists
    if not os.path.exists(settings.GEOIP_DATABASE_PATH):
        return None
    
    try:
        with geoip2.database.Reader(settings.GEOIP_DATABASE_PATH) as reader:
            response = reader.city(ip_address)
            
            return {
                "country": response.country.iso_code,
                "country_name": response.country.name,
                "city": response.city.name,
                "lat": response.location.latitude,
                "lon": response.location.longitude,
                "postal_code": response.postal.code,
                "timezone": response.location.time_zone
            }
            
    except geoip2.errors.AddressNotFoundError:
        return None
    except Exception as e:
        print(f"GeoIP lookup error: {e}")
        return None
