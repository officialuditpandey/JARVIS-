#!/usr/bin/env python3
"""
Maps Query Service for JARVIS - Feature 8
Maps integration with location search and navigation
"""

import os
import sys
import time
import json
import requests
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import urllib.parse

# Add JARVIS backend path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    import folium
    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False
    print("Folium not available - Installing...")
    os.system("pip install folium")

try:
    import geopy
    from geopy.geocoders import Nominatim
    from geopy.distance import geodesic
    GEOPY_AVAILABLE = True
except ImportError:
    GEOPY_AVAILABLE = False
    print("Geopy not available - Installing...")
    os.system("pip install geopy")

class MapsService:
    """Maps service for location search and navigation"""
    
    def __init__(self):
        self.is_active = False
        self.geolocator = None
        self.api_key = None  # Would be configured with actual API key
        
        # Initialize
        self._initialize_maps_service()
        
        print("Maps Service initialized")
    
    def _initialize_maps_service(self):
        """Initialize maps service"""
        try:
            # Initialize geocoder
            if GEOPY_AVAILABLE:
                self.geolocator = Nominatim(user_agent="jarvis_maps")
            
            self.is_active = True
            
        except Exception as e:
            print(f"Maps service initialization failed: {e}")
    
    def search_location(self, query: str) -> Dict[str, Any]:
        """Search for a location"""
        try:
            if not self.geolocator:
                return {
                    'success': False,
                    'error': 'Geocoder not available'
                }
            
            # Search for location
            location = self.geolocator.geocode(query)
            
            if location:
                return {
                    'success': True,
                    'location': {
                        'name': location.address,
                        'latitude': location.latitude,
                        'longitude': location.longitude,
                        'raw': location.raw
                    },
                    'query': query,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'success': False,
                    'error': f'Location not found: {query}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Location search failed: {str(e)}'
            }
    
    def get_coordinates(self, location_name: str) -> Dict[str, Any]:
        """Get coordinates for a location"""
        return self.search_location(location_name)
    
    def calculate_distance(self, origin: str, destination: str) -> Dict[str, Any]:
        """Calculate distance between two locations"""
        try:
            if not self.geolocator:
                return {
                    'success': False,
                    'error': 'Geocoder not available'
                }
            
            # Get coordinates for both locations
            origin_loc = self.geolocator.geocode(origin)
            dest_loc = self.geolocator.geocode(destination)
            
            if origin_loc and dest_loc:
                # Calculate distance
                distance = geodesic(
                    (origin_loc.latitude, origin_loc.longitude),
                    (dest_loc.latitude, dest_loc.longitude)
                )
                
                return {
                    'success': True,
                    'origin': {
                        'name': origin_loc.address,
                        'coordinates': (origin_loc.latitude, origin_loc.longitude)
                    },
                    'destination': {
                        'name': dest_loc.address,
                        'coordinates': (dest_loc.latitude, dest_loc.longitude)
                    },
                    'distance': {
                        'kilometers': distance.kilometers,
                        'miles': distance.miles,
                        'meters': distance.meters
                    },
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'success': False,
                    'error': 'One or both locations not found'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Distance calculation failed: {str(e)}'
            }
    
    def reverse_geocode(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Reverse geocode coordinates to address"""
        try:
            if not self.geolocator:
                return {
                    'success': False,
                    'error': 'Geocoder not available'
                }
            
            location = self.geolocator.reverse((latitude, longitude))
            
            if location:
                return {
                    'success': True,
                    'address': location.address,
                    'coordinates': (latitude, longitude),
                    'raw': location.raw,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'success': False,
                    'error': 'No address found for coordinates'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Reverse geocoding failed: {str(e)}'
            }
    
    def generate_map(self, locations: List[Dict[str, Any]], output_file: str = None) -> Dict[str, Any]:
        """Generate a map with marked locations"""
        try:
            if not FOLIUM_AVAILABLE:
                return {
                    'success': False,
                    'error': 'Folium not available for map generation'
                }
            
            # Create map centered on first location or default
            if locations:
                center_lat = locations[0].get('latitude', 0)
                center_lon = locations[0].get('longitude', 0)
            else:
                center_lat, center_lon = 0, 0
            
            # Create map
            m = folium.Map(location=[center_lat, center_lon], zoom_start=10)
            
            # Add markers for each location
            for i, loc in enumerate(locations):
                lat = loc.get('latitude')
                lon = loc.get('longitude')
                name = loc.get('name', f'Location {i+1}')
                
                if lat and lon:
                    folium.Marker(
                        [lat, lon],
                        popup=name,
                        tooltip=name
                    ).add_to(m)
            
            # Save map
            if not output_file:
                output_file = f"jarvis_map_{int(time.time())}.html"
            
            m.save(output_file)
            
            return {
                'success': True,
                'map_file': output_file,
                'locations_marked': len(locations),
                'center': (center_lat, center_lon),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Map generation failed: {str(e)}'
            }
    
    def get_directions(self, origin: str, destination: str, mode: str = 'driving') -> Dict[str, Any]:
        """Get directions between two locations"""
        try:
            # This would integrate with Google Maps API or similar
            # For now, provide basic information
            
            origin_loc = self.search_location(origin)
            dest_loc = self.search_location(destination)
            
            if origin_loc['success'] and dest_loc['success']:
                distance_calc = self.calculate_distance(origin, destination)
                
                return {
                    'success': True,
                    'origin': origin_loc['location'],
                    'destination': dest_loc['location'],
                    'mode': mode,
                    'distance': distance_calc.get('distance', {}),
                    'estimated_time': self._estimate_travel_time(distance_calc.get('distance', {}), mode),
                    'note': 'Full directions would require Google Maps API integration',
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'success': False,
                    'error': 'Could not find one or both locations'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Directions failed: {str(e)}'
            }
    
    def _estimate_travel_time(self, distance: Dict[str, Any], mode: str) -> Dict[str, Any]:
        """Estimate travel time based on distance and mode"""
        try:
            km = distance.get('kilometers', 0)
            
            # Average speeds (km/h)
            speeds = {
                'driving': 50,
                'walking': 5,
                'cycling': 15,
                'transit': 30
            }
            
            speed = speeds.get(mode, 50)
            hours = km / speed if speed > 0 else 0
            
            return {
                'hours': hours,
                'minutes': hours * 60,
                'seconds': hours * 3600
            }
            
        except:
            return {'hours': 0, 'minutes': 0, 'seconds': 0}
    
    def nearby_search(self, location: str, query: str, radius: int = 1000) -> Dict[str, Any]:
        """Search for places near a location"""
        try:
            # Get location coordinates
            loc_result = self.search_location(location)
            
            if not loc_result['success']:
                return {
                    'success': False,
                    'error': 'Base location not found'
                }
            
            lat = loc_result['location']['latitude']
            lon = loc_result['location']['longitude']
            
            # This would integrate with Google Places API or similar
            # For now, simulate nearby search
            nearby_places = [
                {
                    'name': f'{query} Place 1',
                    'address': f'Near {location}',
                    'latitude': lat + 0.001,
                    'longitude': lon + 0.001,
                    'distance_meters': 150
                },
                {
                    'name': f'{query} Place 2',
                    'address': f'Near {location}',
                    'latitude': lat - 0.001,
                    'longitude': lon + 0.002,
                    'distance_meters': 250
                }
            ]
            
            return {
                'success': True,
                'base_location': loc_result['location'],
                'query': query,
                'radius': radius,
                'places': nearby_places,
                'count': len(nearby_places),
                'note': 'Full nearby search would require Google Places API integration',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Nearby search failed: {str(e)}'
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get maps service status"""
        return {
            'is_active': self.is_active,
            'geocoder_available': self.geolocator is not None,
            'folium_available': FOLIUM_AVAILABLE,
            'geopy_available': GEOPY_AVAILABLE,
            'api_key_configured': self.api_key is not None,
            'last_updated': datetime.now().isoformat()
        }
