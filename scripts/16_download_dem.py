import pystac_client
import planetary_computer
import requests
import os

print("Searching for Copernicus DEM...")
catalog = pystac_client.Client.open(
    "https://planetarycomputer.microsoft.com/api/stac/v1",
    modifier=planetary_computer.sign_inplace,
)

bbox = [31.0, 36.5, 31.8, 37.1] # Manavgat region

search = catalog.search(
    collections=["cop-dem-glo-30"],
    bbox=bbox,
)

items = list(search.item_collection())
print(f"Found {len(items)} DEM items.")

out_dir = r"C:\Users\PC\Desktop\projeler\FireImpact-GIS\data\Sentinel2_Raw"

dem_files = []
for i, item in enumerate(items):
    url = item.assets["data"].href
    out_path = os.path.join(out_dir, f"dem_raw_{i}.tif")
    dem_files.append(out_path)
    if not os.path.exists(out_path):
        print(f"Downloading {out_path}...")
        r = requests.get(url, stream=True)
        with open(out_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    else:
        print(f"Already exists: {out_path}")

print("DEM download complete.")

