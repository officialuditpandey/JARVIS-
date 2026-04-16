#!/usr/bin/env python3
"""
Maps Intelligence Service for JARVIS
Complex location and navigation queries
"""

import os
import sys
import time
import json
import math
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import requests
import geopy
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import folium

# Add JARVIS backend path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    import folium
    FOLIUM_AVAILABLE = True
except ImportError:
    print("folium not available - Installing...")
    os.system("pip install folium")
    try:
        import folium
        FOLIUM_AVAILABLE = True
    except ImportError:
        FOLIUM_AVAILABLE = False

try:
    import geopy
    from geopy.distance import geodesic
    from geopy.geocoders import Nominatim
    GEOPY_AVAILABLE = True
except ImportError:
    print("geopy not available - Installing...")
    os.system("pip install geopy")
    try:
        import geopy
        from geopy.distance import geodesic
        from geopy.geocoders import Nominatim
        GEOPY_AVAILABLE = True
    except ImportError:
        GEOPY_AVAILABLE = False

class MapsIntelligenceService:
    """Maps Intelligence service for location and navigation"""
    
    def __init__(self):
        self.is_active = False
        self.geocoder = None
        self.search_history = []
        self.location_cache = {}
        self.route_cache = {}
        
        # Configuration
        self.cache_expiry = 3600  # 1 hour
        self.max_search_results = 10
        self.default_map_zoom = 13
        
        # User preferences
        self.home_location = None
        self.work_location = None
        self.favorite_places = {}
        
        # API settings
        self.user_agent = "JARVIS_Maps_Intelligence/1.0"
        
        # Initialize
        self._initialize_maps_service()
        
        print("Maps Intelligence Service initialized")
    
    def _initialize_maps_service(self):
        """Initialize maps service components"""
        try:
            if GEOPY_AVAILABLE:
                self.geocoder = Nominatim(user_agent=self.user_agent)
                print("Geocoder initialized")
            
            # Load saved locations
            self._load_saved_locations()
            
        except Exception as e:
            print(f"Maps service initialization failed: {e}")
    
    def _load_saved_locations(self):
        """Load saved locations from file"""
        try:
            locations_file = 'maps_locations.json'
            if os.path.exists(locations_file):
                with open(locations_file, 'r') as f:
                    data = json.load(f)
                    self.home_location = data.get('home_location')
                    self.work_location = data.get('work_location')
                    self.favorite_places = data.get('favorite_places', {})
                print("Loaded saved locations")
        except Exception as e:
            print(f"Failed to load saved locations: {e}")
    
    def _save_locations(self):
        """Save locations to file"""
        try:
            locations_file = 'maps_locations.json'
            data = {
                'home_location': self.home_location,
                'work_location': self.work_location,
                'favorite_places': self.favorite_places,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(locations_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"Failed to save locations: {e}")
    
    def geocode_address(self, address: str) -> Dict[str, Any]:
        """Convert address to coordinates"""
        try:
            if not GEOPY_AVAILABLE:
                return {
                    'success': False,
                    'error': 'Geocoding not available'
                }
            
            # Check cache first
            cache_key = f"geocode_{address.lower()}"
            if cache_key in self.location_cache:
                cached_result = self.location_cache[cache_key]
                if time.time() - cached_result['timestamp'] < self.cache_expiry:
                    return cached_result['data']
            
            # Geocode address
            location = self.geocoder.geocode(address, exactly_one=True, timeout=10)
            
            if location:
                result = {
                    'success': True,
                    'address': location.address,
                    'latitude': location.latitude,
                    'longitude': location.longitude,
                    'raw': location.raw
                }
                
                # Cache result
                self.location_cache[cache_key] = {
                    'data': result,
                    'timestamp': time.time()
                }
                
                return result
            else:
                return {
                    'success': False,
                    'error': f'Address "{address}" not found'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Geocoding failed: {str(e)}'
            }
    
    def reverse_geocode(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Convert coordinates to address"""
        try:
            if not GEOPY_AVAILABLE:
                return {
                    'success': False,
                    'error': 'Reverse geocoding not available'
                }
            
            # Check cache first
            cache_key = f"reverse_{latitude:.6f}_{longitude:.6f}"
            if cache_key in self.location_cache:
                cached_result = self.location_cache[cache_key]
                if time.time() - cached_result['timestamp'] < self.cache_expiry:
                    return cached_result['data']
            
            # Reverse geocode
            location = self.geocoder.reverse((latitude, longitude), exactly_one=True, timeout=10)
            
            if location:
                result = {
                    'success': True,
                    'address': location.address,
                    'latitude': latitude,
                    'longitude': longitude,
                    'raw': location.raw
                }
                
                # Cache result
                self.location_cache[cache_key] = {
                    'data': result,
                    'timestamp': time.time()
                }
                
                return result
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
    
    def calculate_distance(self, origin: str, destination: str) -> Dict[str, Any]:
        """Calculate distance between two locations"""
        try:
            # Geocode both locations
            origin_result = self.geocode_address(origin)
            if not origin_result['success']:
                return {
                    'success': False,
                    'error': f'Origin location not found: {origin}'
                }
            
            dest_result = self.geocode_address(destination)
            if not dest_result['success']:
                return {
                    'success': False,
                    'error': f'Destination location not found: {destination}'
                }
            
            # Calculate distance
            origin_coords = (origin_result['latitude'], origin_result['longitude'])
            dest_coords = (dest_result['latitude'], dest_result['longitude'])
            
            distance_km = geodesic(origin_coords, dest_coords).kilometers
            distance_miles = geodesic(origin_coords, dest_coords).miles
            
            return {
                'success': True,
                'origin': {
                    'address': origin_result['address'],
                    'coordinates': origin_coords
                },
                'destination': {
                    'address': dest_result['address'],
                    'coordinates': dest_coords
                },
                'distance_km': distance_km,
                'distance_miles': distance_miles,
                'bearing': self._calculate_bearing(origin_coords, dest_coords)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Distance calculation failed: {str(e)}'
            }
    
    def _calculate_bearing(self, origin: Tuple[float, float], destination: Tuple[float, float]) -> float:
        """Calculate bearing between two points"""
        try:
            lat1, lon1 = origin
            lat2, lon2 = destination
            
            # Convert to radians
            lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
            
            # Calculate bearing
            dlon = lon2 - lon1
            
            y = math.sin(dlon) * math.cos(lat2)
            x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
            
            bearing = math.atan2(y, x)
            bearing = math.degrees(bearing)
            bearing = (bearing + 360) % 360
            
            return bearing
            
        except:
            return 0.0
    
    def find_nearby_places(self, location: str, place_type: str, radius: float = 5.0) -> Dict[str, Any]:
        """Find nearby places of a specific type"""
        try:
            # Geocode location
            location_result = self.geocode_address(location)
            if not location_result['success']:
                return {
                    'success': False,
                    'error': f'Location not found: {location}'
                }
            
            # Search for nearby places
            search_query = f"{place_type} near {location}"
            
            # This would use a proper places API in production
            # For now, return a mock result
            nearby_places = []
            
            # Generate mock nearby places
            for i in range(min(5, self.max_search_results)):
                # Generate random coordinates within radius
                import random
                angle = random.uniform(0, 2 * math.pi)
                distance = random.uniform(0.1, radius)
                
                lat_offset = distance * math.cos(angle) / 111.32  # Approximate km per degree latitude
                lon_offset = distance * math.sin(angle) / (111.32 * math.cos(math.radians(location_result['latitude'])))
                
                nearby_place = {
                    'name': f"{place_type.title()} {i+1}",
                    'address': f"Near {location}",
                    'latitude': location_result['latitude'] + lat_offset,
                    'longitude': location_result['longitude'] + lon_offset,
                    'distance_km': distance,
                    'type': place_type
                }
                nearby_places.append(nearby_place)
            
            # Sort by distance
            nearby_places.sort(key=lambda x: x['distance_km'])
            
            return {
                'success': True,
                'location': location_result['address'],
                'search_type': place_type,
                'radius_km': radius,
                'places_found': len(nearby_places),
                'places': nearby_places
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Nearby places search failed: {str(e)}'
            }
    
    def get_directions(self, origin: str, destination: str, mode: str = 'driving') -> Dict[str, Any]:
        """Get directions between two locations"""
        try:
            # Geocode both locations
            origin_result = self.geocode_address(origin)
            if not origin_result['success']:
                return {
                    'success': False,
                    'error': f'Origin location not found: {origin}'
                }
            
            dest_result = self.geocode_address(destination)
            if not dest_result['success']:
                return {
                    'success': False,
                    'error': f'Destination location not found: {destination}'
                }
            
            # Calculate route (simplified - would use proper routing API in production)
            distance_km = geodesic(
                (origin_result['latitude'], origin_result['longitude']),
                (dest_result['latitude'], dest_result['longitude'])
            ).kilometers
            
            # Estimate time based on mode
            speed_map = {
                'driving': 50,    # km/h
                'walking': 5,     # km/h
                'cycling': 15,    # km/h
                'transit': 30     # km/h
            }
            
            speed = speed_map.get(mode, 50)
            time_minutes = (distance_km / speed) * 60
            
            # Generate mock route steps
            route_steps = [
                {
                    'instruction': f'Head {self._get_direction(origin_result, dest_result)} from {origin}',
                    'distance_km': distance_km * 0.3,
                    'time_minutes': time_minutes * 0.3
                },
                {
                    'instruction': f'Continue toward {destination}',
                    'distance_km': distance_km * 0.4,
                    'time_minutes': time_minutes * 0.4
                },
                {
                    'instruction': f'Arrive at {destination}',
                    'distance_km': distance_km * 0.3,
                    'time_minutes': time_minutes * 0.3
                }
            ]
            
            return {
                'success': True,
                'origin': origin_result['address'],
                'destination': dest_result['address'],
                'mode': mode,
                'distance_km': distance_km,
                'distance_miles': distance_km * 0.621371,
                'time_minutes': time_minutes,
                'time_hours': time_minutes / 60,
                'steps': route_steps
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Directions failed: {str(e)}'
            }
    
    def _get_direction(self, origin_result: Dict[str, Any], dest_result: Dict[str, Any]) -> str:
        """Get general direction between two points"""
        try:
            bearing = self._calculate_bearing(
                (origin_result['latitude'], origin_result['longitude']),
                (dest_result['latitude'], dest_result['longitude'])
            )
            
            # Convert bearing to cardinal direction
            directions = ['North', 'Northeast', 'East', 'Southeast', 'South', 'Southwest', 'West', 'Northwest']
            index = round(bearing / 45) % 8
            return directions[index]
            
        except:
            return 'toward'
    
    def create_map(self, locations: List[Dict[str, Any]], save_path: str = None) -> Dict[str, Any]:
        """Create a map with marked locations"""
        try:
            if not FOLIUM_AVAILABLE:
                return {
                    'success': False,
                    'error': 'Map creation not available'
                }
            
            if not locations:
                return {
                    'success': False,
                    'error': 'No locations provided'
                }
            
            # Calculate map center
            avg_lat = sum(loc['latitude'] for loc in locations) / len(locations)
            avg_lon = sum(loc['longitude'] for loc in locations) / len(locations)
            
            # Create map
            m = folium.Map(location=[avg_lat, avg_lon], zoom_start=self.default_map_zoom)
            
            # Add markers
            for i, location in enumerate(locations):
                folium.Marker(
                    [location['latitude'], location['longitude']],
                    popup=location.get('name', f'Location {i+1}'),
                    tooltip=location.get('name', f'Location {i+1}')
                ).add_to(m)
            
            # Draw lines between consecutive locations
            if len(locations) > 1:
                coordinates = [[loc['latitude'], loc['longitude']] for loc in locations]
                folium.PolyLine(coordinates, color='blue', weight=2, opacity=0.8).add_to(m)
            
            # Save map
            if save_path is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                save_path = f'maps/jarvis_map_{timestamp}.html'
            
            os.makedirs('maps', exist_ok=True)
            m.save(save_path)
            
            return {
                'success': True,
                'map_file': save_path,
                'locations_marked': len(locations),
                'center': [avg_lat, avg_lon],
                'message': f'Map saved to {save_path}'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Map creation failed: {str(e)}'
            }
    
    def search_location(self, query: str) -> Dict[str, Any]:
        """Search for a location"""
        try:
            # Use geocoding to search
            result = self.geocode_address(query)
            
            if result['success']:
                # Add to search history
                search_entry = {
                    'query': query,
                    'result': result,
                    'timestamp': datetime.now().isoformat()
                }
                self.search_history.append(search_entry)
                
                # Keep only last 100 searches
                if len(self.search_history) > 100:
                    self.search_history = self.search_history[-100:]
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Location search failed: {str(e)}'
            }
    
    def set_home_location(self, address: str) -> Dict[str, Any]:
        """Set home location"""
        try:
            result = self.geocode_address(address)
            if result['success']:
                self.home_location = {
                    'address': result['address'],
                    'latitude': result['latitude'],
                    'longitude': result['longitude']
                }
                self._save_locations()
                
                return {
                    'success': True,
                    'home_location': self.home_location,
                    'message': 'Home location set successfully'
                }
            else:
                return result
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to set home location: {str(e)}'
            }
    
    def set_work_location(self, address: str) -> Dict[str, Any]:
        """Set work location"""
        try:
            result = self.geocode_address(address)
            if result['success']:
                self.work_location = {
                    'address': result['address'],
                    'latitude': result['latitude'],
                    'longitude': result['longitude']
                }
                self._save_locations()
                
                return {
                    'success': True,
                    'work_location': self.work_location,
                    'message': 'Work location set successfully'
                }
            else:
                return result
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to set work location: {str(e)}'
            }
    
    def add_favorite_place(self, name: str, address: str) -> Dict[str, Any]:
        """Add a favorite place"""
        try:
            result = self.geocode_address(address)
            if result['success']:
                self.favorite_places[name] = {
                    'address': result['address'],
                    'latitude': result['latitude'],
                    'longitude': result['longitude'],
                    'added_at': datetime.now().isoformat()
                }
                self._save_locations()
                
                return {
                    'success': True,
                    'place_name': name,
                    'place_info': self.favorite_places[name],
                    'message': f'Favorite place "{name}" added successfully'
                }
            else:
                return result
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to add favorite place: {str(e)}'
            }
    
    def get_commute_info(self) -> Dict[str, Any]:
        """Get commute information between home and work"""
        try:
            if not self.home_location or not self.work_location:
                return {
                    'success': False,
                    'error': 'Home and work locations not set'
                }
            
            # Calculate distance and directions
            origin = f"{self.home_location['latitude']},{self.home_location['longitude']}"
            destination = f"{self.work_location['latitude']},{self.work_location['longitude']}"
            
            directions = self.get_directions(origin, destination)
            
            return {
                'success': True,
                'home_address': self.home_location['address'],
                'work_address': self.work_location['address'],
                'commute_info': directions
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Commute info failed: {str(e)}'
            }
    
    def get_search_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent search history"""
        return self.search_history[-limit:]
    
    def get_saved_locations(self) -> Dict[str, Any]:
        """Get all saved locations"""
        return {
            'home_location': self.home_location,
            'work_location': self.work_location,
            'favorite_places': self.favorite_places
        }
    
    def clear_cache(self):
        """Clear location cache"""
        self.location_cache.clear()
        self.route_cache.clear()
        print("Location cache cleared")
    
    def get_status(self) -> Dict[str, Any]:
        """Get maps intelligence service status"""
        return {
            'is_active': self.is_active,
            'geopy_available': GEOPY_AVAILABLE,
            'folium_available': FOLIUM_AVAILABLE,
            'home_location_set': self.home_location is not None,
            'work_location_set': self.work_location is not None,
            'favorite_places_count': len(self.favorite_places),
            'cache_size': len(self.location_cache),
            'search_history_count': len(self.search_history),
            'last_updated': datetime.now().isoformat()
        }
