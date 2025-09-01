import googlemaps
from datetime import datetime
import logging
from dotenv import load_dotenv
import os

class GoogleDirectionsClient:
    """
    Wrapper for Google Maps Directions API using googlemaps Python client library.
    """
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("MAPS_API_KEY")
        if not api_key:
            raise ValueError("MAPS_API_KEY not found in environment. Check your .env file.")
        logging.info("[GoogleDirectionsClient] Initializing client...")
        self.client = googlemaps.Client(key=api_key)
        logging.info("[GoogleDirectionsClient] Client initialized.")


    def get_directions(self,
                       origin,
                       destination,
                       mode="driving",
                       waypoints=None,
                       depart_time=None,
                       arrival_time=None,
                       optimize_waypoints=False,
                       alternatives=False,
                       avoid=None,
                       traffic_model=None,
                       transit_mode=None,
                       transit_routing_preference=None,
                       units="metric",
                       language=None) -> dict:
        """
        Fetch directions between origin and destination with optional parameters.
        """
        logging.info(f"[GoogleDirectionsClient] Requesting directions from {origin} to {destination}...")
        directions = self.client.directions(
            origin=origin,
            destination=destination,
            mode=mode,
            waypoints=waypoints,
            optimize_waypoints=optimize_waypoints,
            alternatives=alternatives,
            avoid=avoid,
            departure_time=depart_time or datetime.now(),
            arrival_time=arrival_time,
            traffic_model=traffic_model,
            transit_mode=transit_mode,
            transit_routing_preference=transit_routing_preference,
            units=units,
            language=language
        )
        logging.info(f"[GoogleDirectionsClient] Retrieved {len(directions)} route(s).")
        return directions
