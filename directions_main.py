from apis.directions_api import GoogleDirectionsClient

def main():
    client = GoogleDirectionsClient()

    # Simple one-leg route example
    origin = "Connaught Place, New Delhi"
    destination = "Hauz Khas, New Delhi"
    route = client.get_directions(origin, destination, mode="driving")
    print("Route summary:", route[0]['legs'][0]['distance'], route[0]['legs'][0]['duration'])

    # Example with waypoints and optimization
    waypoints = ["India Gate, New Delhi", "Red Fort, New Delhi"]
    optimized_route = client.get_directions(
        origin, destination, mode="driving",
        waypoints=waypoints,
        optimize_waypoints=True
    )
    print("Optimized waypoint order:", optimized_route[0].get('waypoint_order'))

if __name__ == "__main__":
    main()