import requests
from typing import List, Optional

from dotenv import load_dotenv
import os

class GooglePlacesClient:
    """
    Wrapper class for Google Places API (v1).
    Supports searching nearby places, text search, and place details.
    """

    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("MAPS_API_KEY")
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
        url = f"{self.base_url}/places/{place_id}"
        response = requests.get(url, headers=self._headers())
        response.raise_for_status()
        return response.json()

