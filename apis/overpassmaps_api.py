import requests
import logging

class OSMOverpassClient:
    """
    Client class to interact with OpenStreetMap data using the Overpass API.
    """

    def __init__(self, base_url: str = "https://overpass-api.de/api/interpreter"):
        """
        Initialize the OSMOverpassClient with a base Overpass API endpoint.
        """
        self.base_url = base_url
        logging.info(f"[OSMOverpassClient] Initialized with base URL: {self.base_url}")

    def query(self, overpass_query: str) -> dict:
        """
        Executes an Overpass QL query and returns the JSON result.
        """
        logging.info("[OSMOverpassClient] Executing query...")
        response = requests.post(self.base_url, data={"data": overpass_query})

        if response.status_code == 200:
            logging.info("[OSMOverpassClient] Query successful.")
            return response.json()
        else:
            logging.error(f"[OSMOverpassClient] Query failed with status: {response.status_code}")
            response.raise_for_status()

    def find_places(self, lat: float, lon: float, radius: int = 1000, place_type: str = "cafe") -> list:
        """
        Finds nearby places of a given type (like cafes, restaurants) around a point.
        """
        logging.info(f"[OSMOverpassClient] Searching for {place_type} near ({lat}, {lon}) within {radius}m.")
        query = f"""
        [out:json];
        node["amenity"="{place_type}"](around:{radius},{lat},{lon});
        out;
        """
        data = self.query(query)

        places = []
        for element in data.get("elements", []):
            name = element.get("tags", {}).get("name", "Unnamed")
            lat = element.get("lat")
            lon = element.get("lon")
            places.append({"name": name, "lat": lat, "lon": lon})

        logging.info(f"[OSMOverpassClient] Found {len(places)} {place_type}(s).")
        return places
