from apis.routes_api import GoogleRoutesClient
import json


import os
from dotenv import load_dotenv
load_dotenv()

def main():
    client = GoogleRoutesClient(api_key=os.getenv("MAPS_API_KEY"))

    # Simple one-leg route example
    origin = {"location": {"latLng": {"latitude": 28.6315, "longitude": 77.2167}}}   # Connaught Place
    destination = {"location": {"latLng": {"latitude": 28.5494, "longitude": 77.2001}}}  # Hauz Khas

    route = client.get_route(origin, destination, travel_mode="TRANSIT")
    print("Simple route result:")
    print(json.dumps(route, indent=2))

    # Example with waypoints
    waypoints = [
        {"location": {"latLng": {"latitude": 28.6129, "longitude": 77.2295}}},  # India Gate
        {"location": {"latLng": {"latitude": 28.6562, "longitude": 77.2410}}}   # Red Fort
    ]

    optimized_route = client.get_route(origin, destination, travel_mode="DRIVE", intermediates=waypoints)
    print("\nRoute with intermediates (waypoints):")
    # print(json.dumps(optimized_route, indent=2))


if __name__ == "__main__":
    main()
