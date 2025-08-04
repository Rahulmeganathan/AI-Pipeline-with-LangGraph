import requests
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass
from src.config import get_settings


@dataclass
class WeatherData:
    """Data class for weather information."""
    location: str
    temperature: float
    description: str
    humidity: int
    wind_speed: float
    pressure: int
    feels_like: float
    visibility: int


class WeatherService:
    """Service for fetching weather data from OpenWeatherMap API."""
    
    def __init__(self):
        self.settings = get_settings()
        self.base_url = "http://api.openweathermap.org/data/2.5"
        self.api_key = self.settings.openweather_api_key
    
    def extract_location_from_query(self, query: str) -> Optional[str]:
        """Extract location from a natural language query."""
        # Simple location extraction - in a real app, you might use NER
        weather_keywords = ["weather", "temperature", "forecast", "climate"]
        query_lower = query.lower()
        
        # Check if it's a weather query
        if not any(keyword in query_lower for keyword in weather_keywords):
            return None
        
        # Simple location extraction (this could be improved with NLP)
        # Look for common location patterns
        import re
        
        # Common city patterns
        patterns = [
            r"(?:weather|temperature|forecast|climate)\s+(?:in|at|for)\s+([A-Za-z\s]+?)(?:\?|$)",  # weather in/at London
            r"(?:in|at)\s+([A-Za-z\s]+?)(?:\?|$|\s+weather|\s+forecast)",  # in/at London weather
            r"([A-Za-z]+)(?:\?|$)"  # Just the city name
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query_lower)
            if match:
                location = match.group(1).strip()
                if location and len(location) > 1:
                    return location.title()
        
        return None
    
    def get_weather_by_location(self, location: str) -> WeatherData:
        """Fetch weather data for a specific location."""
        try:
            # First, get coordinates for the location
            geocoding_url = f"http://api.openweathermap.org/geo/1.0/direct"
            params = {
                "q": location,
                "limit": 1,
                "appid": self.api_key
            }
            
            response = requests.get(geocoding_url, params=params, timeout=10)
            response.raise_for_status()
            
            geocoding_data = response.json()
            if not geocoding_data:
                raise ValueError(f"Location '{location}' not found")
            
            lat = geocoding_data[0]["lat"]
            lon = geocoding_data[0]["lon"]
            
            # Get weather data using coordinates
            weather_url = f"{self.base_url}/weather"
            params = {
                "lat": lat,
                "lon": lon,
                "appid": self.api_key,
                "units": "metric"  # Use metric units
            }
            
            response = requests.get(weather_url, params=params, timeout=10)
            response.raise_for_status()
            
            weather_data = response.json()
            
            return WeatherData(
                location=location,
                temperature=weather_data["main"]["temp"],
                description=weather_data["weather"][0]["description"],
                humidity=weather_data["main"]["humidity"],
                wind_speed=weather_data["wind"]["speed"],
                pressure=weather_data["main"]["pressure"],
                feels_like=weather_data["main"]["feels_like"],
                visibility=weather_data.get("visibility", 0) // 1000  # Convert to km
            )
            
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch weather data: {str(e)}")
        except (KeyError, IndexError) as e:
            raise Exception(f"Invalid weather data format: {str(e)}")
        except Exception as e:
            raise Exception(f"Error processing weather data: {str(e)}")
    
    def format_weather_response(self, weather_data: WeatherData) -> str:
        """Format weather data into a natural language response."""
        return f"""Current weather in {weather_data.location}:
• Temperature: {weather_data.temperature}°C (feels like {weather_data.feels_like}°C)
• Conditions: {weather_data.description.capitalize()}
• Humidity: {weather_data.humidity}%
• Wind Speed: {weather_data.wind_speed} m/s
• Pressure: {weather_data.pressure} hPa
• Visibility: {weather_data.visibility} km"""
    
    def process_weather_query(self, query: str) -> Dict[str, Any]:
        """Process a weather-related query and return formatted response."""
        location = self.extract_location_from_query(query)
        
        if not location:
            return {
                "type": "weather",
                "success": False,
                "error": "Could not extract location from query. Please specify a location.",
                "query": query
            }
        
        try:
            weather_data = self.get_weather_by_location(location)
            formatted_response = self.format_weather_response(weather_data)
            
            return {
                "type": "weather",
                "success": True,
                "location": location,
                "weather_data": weather_data,
                "response": formatted_response,
                "query": query
            }
            
        except Exception as e:
            return {
                "type": "weather",
                "success": False,
                "error": str(e),
                "query": query
            } 