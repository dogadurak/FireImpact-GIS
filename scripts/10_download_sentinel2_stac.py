import os
import requests
from pystac_client import Client
import planetary_computer

print("Microsoft Planetary Computer uzerinden %100 bilimsel (16-bit) Sentinel-2 verileri araniyor...")

# Manavgat Bounding Box [min_lon, min_lat, max_lon, max_lat]
bbox = [31.3, 36.7, 31.6, 37.0]

# STAC API connection
catalog = Client.open(
    "https://planetarycomputer.microsoft.com/api/stac/v1",
    modifier=planetary_computer.sign_inplace,
)

# Klasoru olustur
out_dir = r"C:\Users\PC\Desktop\projeler\FireImpact-GIS\data\Sentinel2_Raw"
os.makedirs(out_dir, exist_ok=True)

def download_asset(asset, output_path):
    if os.path.exists(output_path):
        print(f"Zaten mevcut: {output_path}")
        return
    print(f"Indiriliyor -> {output_path}")
    response = requests.get(asset.href, stream=True)
    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    print("Indirme tamamlandi!")

# 1. Yangin Oncesi (Pre-fire: July 2021)
print("Yangin Oncesi (Pre-fire) uydusu araniyor...")
search_pre = catalog.search(
    collections=["sentinel-2-l2a"],
    bbox=bbox,
    datetime="2021-07-01/2021-07-27",
    query={"eo:cloud_cover": {"lt": 10}}
)
items_pre = list(search_pre.items())
if items_pre:
    # Sort by cloud cover
    best_pre = sorted(items_pre, key=lambda x: x.properties["eo:cloud_cover"])[0]
    print(f"Bulundu: {best_pre.id} (Tarih: {best_pre.datetime})")
    
    # Download B08 (NIR), B12 (SWIR2), SCL, and TCI (visual)
    b8_asset = best_pre.assets["B08"]
    b12_asset = best_pre.assets["B12"]
    scl_asset = best_pre.assets["SCL"]
    tci_asset = best_pre.assets["visual"]
    
    download_asset(b8_asset, os.path.join(out_dir, "pre_fire_B08.tif"))
    download_asset(b12_asset, os.path.join(out_dir, "pre_fire_B12.tif"))
    download_asset(scl_asset, os.path.join(out_dir, "pre_fire_SCL.tif"))
    download_asset(tci_asset, os.path.join(out_dir, "pre_fire_TCI.tif"))
else:
    print("Uygun goruntu bulunamadi!")

# 2. Yangin Sonrasi (Post-fire: August 2021)
print("\nYangin Sonrasi (Post-fire) uydusu araniyor...")
search_post = catalog.search(
    collections=["sentinel-2-l2a"],
    bbox=bbox,
    datetime="2021-08-10/2021-08-30",
    query={"eo:cloud_cover": {"lt": 10}}
)
items_post = list(search_post.items())
if items_post:
    best_post = sorted(items_post, key=lambda x: x.properties["eo:cloud_cover"])[0]
    print(f"Bulundu: {best_post.id} (Tarih: {best_post.datetime})")
    
    b8_asset = best_post.assets["B08"]
    b12_asset = best_post.assets["B12"]
    scl_asset = best_post.assets["SCL"]
    tci_asset = best_post.assets["visual"]
    
    download_asset(b8_asset, os.path.join(out_dir, "post_fire_B08.tif"))
    download_asset(b12_asset, os.path.join(out_dir, "post_fire_B12.tif"))
    download_asset(scl_asset, os.path.join(out_dir, "post_fire_SCL.tif"))
    download_asset(tci_asset, os.path.join(out_dir, "post_fire_TCI.tif"))
else:
    print("Uygun goruntu bulunamadi!")

print("\nHarika! Bilimsel (Raw) TIF dosyalari ArcPy analizine hazir.")
