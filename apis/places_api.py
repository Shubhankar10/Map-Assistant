import requests
from typing import List, Optional, Tuple

class GooglePlacesClient:
    """
    Wrapper class for Google Places API (v1).
    Supports searching nearby places, text search, and place details.
    """

    def __init__(self,api_key: str = None):
        self.api_key = api_key
        self.base_url = "https://places.googleapis.com/v1"

    def _headers(self) -> dict:
        """Return headers required by Google Places API."""
        return {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": "*",  # request all available fields
        }

    def search_nearby(self, lat: float, lon: float, radius: int, place_type: Optional[str] = None) -> List[dict]:
        """
        Search nearby places by coordinates and radius.
        Example: cafes within 1000m of (lat, lon).
        """
        url = f"{self.base_url}/places:searchNearby"
        payload = {
            "locationRestriction": {
                "circle": {
                    "center": {"latitude": lat, "longitude": lon},
                    "radius": radius
                }
            }
        }
        
        if place_type:
            payload["includedTypes"] = [place_type]

        response = requests.post(url, headers=self._headers(), json=payload)
        response.raise_for_status()
        return response.json().get("places", [])

    def text_search(self, query: str) -> List[dict]:
        """
        Search for places by text query (e.g., 'best pizza in New York').
        """
        url = f"{self.base_url}/places:searchText"
        payload = {"textQuery": query}

        response = requests.post(url, headers=self._headers(), json=payload)
        response.raise_for_status()
        return response.json().get("places", [])

    def get_place_details(self, place_id: str) -> dict:
        """
        Fetch detailed information about a place using its place_id.
        """
        # url = f"{self.base_url}/places/{place_id}"
        url = f"{self.base_url}/places/ChIJ49OFXeTjDDkRjpYCSUGTE2k"
        response = requests.get(url, headers=self._headers())
        response.raise_for_status()
        return response.json()
    
    def reverse_geocode(self, lat: float, lon: float) -> Optional[str]:
        """
        Converts (lat, lon) coordinates into a human-readable address.
        Uses the standard Google Geocoding API.
        """
        # Note: This is the v3 Geocoding API endpoint, not the v1 Places
        base_url = "https://maps.googleapis.com/maps/api/geocode/json" 
        params = {
            "latlng": f"{lat},{lon}",
            "key": self.api_key,
            # Ask for a general area, not a specific street address
            "result_type": "political|sublocality|locality", 
        }
        
        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "OK" and data.get("results"):
                # Return the first, most relevant address
                return data["results"][0]["formatted_address"]
            else:
                return f"{lat},{lon}" # Fallback to coordinates
        except requests.RequestException as e:
            print(f"Error calling Reverse Geocode API: {e}")
            return f"{lat},{lon}"