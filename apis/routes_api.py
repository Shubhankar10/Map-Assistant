import requests
import json


class GoogleRoutesClient:
    """
    Client to interact with the Google Maps Routes API (v2).
    """

    def __init__(self,api_key: str = None):
        """
        Initialize the Routes client with the API key.
        """
        
        self.api_key = api_key
        if not self.api_key:
            raise ValueError("MAPS_API_KEY not found in environment. Check your .env file.")
        
        self.base_url = "https://routes.googleapis.com/directions/v2:computeRoutes"

    def get_route(self, origin: dict, destination: dict, travel_mode: str = "DRIVE", intermediates: list = None) -> dict:
        """
        Compute a route between origin and destination, optionally with waypoints.

        Args:
            origin (dict): {"location": {"latLng": {"latitude": <lat>, "longitude": <lng>}}}
            destination (dict): same format as origin
            travel_mode (str): "DRIVE", "BICYCLE", or "WALK"
            intermediates (list): list of dicts in same format as origin/destination

        Returns:
            dict: JSON response from Routes API
        """
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": "routes.duration,routes.distanceMeters,routes.polyline,routes.legs"
        }

        payload = {
            "origin": origin,
            "destination": destination,
            "travelMode": travel_mode
        }

        if intermediates:
            payload["intermediates"] = intermediates

        response = requests.post(self.base_url, headers=headers, data=json.dumps(payload))
        if response.status_code != 200:
            raise Exception(f"Routes API Error: {response.status_code}, {response.text}")

        return response.json()
