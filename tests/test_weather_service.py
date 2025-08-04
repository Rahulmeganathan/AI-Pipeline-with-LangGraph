import pytest
from unittest.mock import Mock, patch
from src.weather.weather_service import WeatherService, WeatherData


class TestWeatherService:
    """Test cases for WeatherService."""
    
    @pytest.fixture
    def weather_service(self):
        """Create a WeatherService instance for testing."""
        with patch('src.config.get_settings') as mock_settings:
            mock_settings.return_value.openweather_api_key = "test_api_key"
            return WeatherService()
    
    def test_extract_location_from_query_weather(self, weather_service):
        """Test location extraction from weather queries."""
        # Test weather queries
        assert weather_service.extract_location_from_query("What's the weather in New York?") == "New York"
        assert weather_service.extract_location_from_query("Weather in London") == "London"
        assert weather_service.extract_location_from_query("Temperature in Tokyo") == "Tokyo"
        assert weather_service.extract_location_from_query("Forecast for Paris") == "Paris"
    
    def test_extract_location_from_query_non_weather(self, weather_service):
        """Test location extraction from non-weather queries."""
        # Test non-weather queries
        assert weather_service.extract_location_from_query("What is machine learning?") is None
        assert weather_service.extract_location_from_query("Tell me about Python") is None
        assert weather_service.extract_location_from_query("How to cook pasta") is None
    
    @patch('requests.get')
    def test_get_weather_by_location_success(self, mock_get, weather_service):
        """Test successful weather data retrieval."""
        # Mock geocoding response
        mock_geocoding_response = Mock()
        mock_geocoding_response.json.return_value = [
            {"lat": 40.7128, "lon": -74.0060, "name": "New York"}
        ]
        mock_geocoding_response.raise_for_status.return_value = None
        
        # Mock weather response
        mock_weather_response = Mock()
        mock_weather_response.json.return_value = {
            "main": {
                "temp": 20.5,
                "feels_like": 22.0,
                "humidity": 65,
                "pressure": 1013
            },
            "weather": [{"description": "scattered clouds"}],
            "wind": {"speed": 5.2},
            "visibility": 10000
        }
        mock_weather_response.raise_for_status.return_value = None
        
        # Configure mock to return different responses for different calls
        mock_get.side_effect = [mock_geocoding_response, mock_weather_response]
        
        result = weather_service.get_weather_by_location("New York")
        
        assert isinstance(result, WeatherData)
        assert result.location == "New York"
        assert result.temperature == 20.5
        assert result.description == "scattered clouds"
        assert result.humidity == 65
        assert result.wind_speed == 5.2
        assert result.pressure == 1013
        assert result.feels_like == 22.0
        assert result.visibility == 10
    
    @patch('requests.get')
    def test_get_weather_by_location_geocoding_error(self, mock_get, weather_service):
        """Test weather retrieval with geocoding error."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("Geocoding API error")
        
        mock_get.return_value = mock_response
        
        with pytest.raises(Exception) as exc_info:
            weather_service.get_weather_by_location("Invalid Location")
        
        assert "Failed to fetch weather data" in str(exc_info.value)
    
    @patch('requests.get')
    def test_get_weather_by_location_empty_geocoding(self, mock_get, weather_service):
        """Test weather retrieval with empty geocoding response."""
        mock_response = Mock()
        mock_response.json.return_value = []
        mock_response.raise_for_status.return_value = None
        
        mock_get.return_value = mock_response
        
        with pytest.raises(Exception) as exc_info:
            weather_service.get_weather_by_location("Unknown Location")
        
        assert "Location 'Unknown Location' not found" in str(exc_info.value)
    
    def test_format_weather_response(self, weather_service):
        """Test weather response formatting."""
        weather_data = WeatherData(
            location="London",
            temperature=15.5,
            description="light rain",
            humidity=80,
            wind_speed=3.5,
            pressure=1005,
            feels_like=14.0,
            visibility=8
        )
        
        formatted = weather_service.format_weather_response(weather_data)
        
        assert "London" in formatted
        assert "15.5°C" in formatted
        assert "light rain" in formatted
        assert "80%" in formatted
        assert "3.5 m/s" in formatted
        assert "1005 hPa" in formatted
        assert "8 km" in formatted
    
    @patch('src.weather.weather_service.WeatherService.get_weather_by_location')
    def test_process_weather_query_success(self, mock_get_weather, weather_service):
        """Test successful weather query processing."""
        # Mock weather data
        mock_weather_data = WeatherData(
            location="Paris",
            temperature=18.0,
            description="partly cloudy",
            humidity=70,
            wind_speed=4.0,
            pressure=1010,
            feels_like=17.5,
            visibility=10
        )
        
        mock_get_weather.return_value = mock_weather_data
        
        result = weather_service.process_weather_query("What's the weather in Paris?")
        
        assert result["type"] == "weather"
        assert result["success"] is True
        assert result["location"] == "Paris"
        assert "Paris" in result["response"]
        assert "18.0°C" in result["response"]
    
    def test_process_weather_query_no_location(self, weather_service):
        """Test weather query processing with no location."""
        result = weather_service.process_weather_query("What is machine learning?")
        
        assert result["type"] == "weather"
        assert result["success"] is False
        assert "Could not extract location" in result["error"]
    
    @patch('src.weather.weather_service.WeatherService.get_weather_by_location')
    def test_process_weather_query_api_error(self, mock_get_weather, weather_service):
        """Test weather query processing with API error."""
        mock_get_weather.side_effect = Exception("API Error")
        
        result = weather_service.process_weather_query("What's the weather in Tokyo?")
        
        assert result["type"] == "weather"
        assert result["success"] is False
        assert "API Error" in result["error"]


if __name__ == "__main__":
    pytest.main([__file__]) 