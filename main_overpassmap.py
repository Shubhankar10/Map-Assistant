from apis.overpassmaps_api import OSMOverpassClient

def main():
    client = OSMOverpassClient()
    
    # Example: Find cafes near Connaught Place, Delhi (lat=28.6315, lon=77.2167)
    # results = client.find_places(lat=28.6315, lon=77.2167, radius=800, place_type="cafe")
    # Bhilai CC 
    results = client.find_places(lat=21.1866, lon=81.3429, radius=800, place_type="cafe")


    for r in results:
        print(f"Name: {r['name']} | Location: ({r['lat']}, {r['lon']})")

if __name__ == "__main__":
    main()
