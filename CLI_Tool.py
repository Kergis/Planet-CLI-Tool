import os
import os
import time
import json
import requests
import argparse

# pretty printing
def p(data):
    print(json.dumps(data, indent=2))

# main tool function
def run_cli_tool(api_key, start_time, end_time, geojson_path, output_dir="downloads"):

    # load geometry from geojson
    with open(geojson_path, "r") as geojson_file:
        geojson_data = json.load(geojson_file)
    geojson_geometry = geojson_data['features'][0]['geometry']

    # start session
    session = requests.Session()
    session.auth = (api_key, "")

    url_base = "https://api.planet.com/data/v1"
    res = session.get(url_base)
    print(res)

    # setup filters (AOI and TOI, then into combined filter)
    geometry_filter = {
        "type": "GeometryFilter",
        "field_name": "geometry",
        "config": geojson_geometry
    }

    date_range_filter = {
        "type": "DateRangeFilter",
        "field_name": "acquired",
        "config": {
            "gte": start_time,
            "lte": end_time
        }
    }

    # combine with the and filter
    combined_filter = {
        "type": "AndFilter",
        "config": [geometry_filter, date_range_filter]
    }
    
    # setup combined request 
    search_request = {
        "item_types": ["PSScene"],
        "asset_types": ["ortho_visual"],
        "filter": combined_filter
    }

    quick_url = f"{url_base}/quick-search"
    search_result = session.post(quick_url, json=search_request)

    # pull item IDs from the search results, put into list
    features = search_result.json().get("features", [])
    item_ids = [feature["id"] for feature in features]

    print(f"found {len(features)} results.")

    # put together order request according to given parameters (clip to user AOI geojson)
    order_request = {
    "name": "aoi_order",
    "products": [{
        "item_ids": item_ids,
        "item_type": "PSScene",
        "product_bundle": "visual"
    }],
    "tools": [{
        "clip": {
            "aoi": geojson_geometry
            }
        }]
    }

    # orders endpoint
    orders_url = "https://api.planet.com/compute/ops/orders/v2"
    p(order_request)

    order_response = session.post(orders_url, json=order_request)
    print("order response:", order_response.status_code)
    print(order_response.text)
    order_response.raise_for_status()
    
    order_url = order_response.json()["_links"]["_self"]
    print(f"order submitted: {order_url}")

    # information about order
    while True:
        r = session.get(order_url)
        state = r.json()["state"]
        print(f"order state: {state}")
        if state == "success":
            break
        elif state == "failed":
            raise Exception("rrder failed")
        time.sleep(10)

    # download results into our directory 
    os.makedirs(output_dir, exist_ok=True)
    order_info = session.get(order_url).json()
    results = order_info["_links"]["results"]
    for result in results:
        result_url = result["location"]
        filename = os.path.join(output_dir, os.path.basename(result_url))
        print(f"downloading {result_url} to {filename}")
        with session.get(result_url, stream=True) as r:
            r.raise_for_status()
            with open(filename, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
                    
# main function sestup with inputs from argparse for CLI usability 
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Planet CLI Tool: Quick Search and download")
    parser.add_argument("--api-key", required=True, help="Your Planet API key")
    parser.add_argument("--start-time", required=True, help="Start time in ISO 8601 format")
    parser.add_argument("--end-time", required=True, help="End time in ISO 8601 format")
    parser.add_argument("--geojson", required=True, help="Path to area of interest (AOI) in GeoJSON format")
    
    args = parser.parse_args()

    # run it
    run_cli_tool(
        api_key=args.api_key,
        start_time=args.start_time,
        end_time=args.end_time,
        geojson_path=args.geojson,
    )
