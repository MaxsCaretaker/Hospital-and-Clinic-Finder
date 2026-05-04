import requests

def search_hospitals(city):
    # Step 1: Get coordinates for the city
    geo_url = "https://nominatim.openstreetmap.org/search"
    geo_params = {
        "q": city,
        "format": "json",
        "limit": 1
    }
    headers = {"User-Agent": "hospital-finder-app"}

    geo_response = requests.get(geo_url, params=geo_params, headers=headers)
    geo_data = geo_response.json()

    if not geo_data:
        print("City not found.")
        return

    lat = float(geo_data[0]["lat"])
    lon = float(geo_data[0]["lon"])
    print(f"Found city: {city} at ({lat}, {lon})")

    # Step 2: Search hospitals near those coordinates
    search_url = "https://nominatim.openstreetmap.org/search"
    search_params = {
        "q": "hospital",
        "format": "json",
        "limit": 10,
        "viewbox": f"{lon-0.3},{lat+0.3},{lon+0.3},{lat-0.3}",
        "bounded": 1
    }

    search_response = requests.get(search_url, params=search_params, headers=headers)
    results = search_response.json()

    print(f"Found {len(results)} hospitals near {city}:")
    for place in results:
        print(f"  - {place.get('display_name', 'Unknown')[:80]}")

search_hospitals("Los Angeles")