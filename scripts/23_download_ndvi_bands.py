import os
import requests
from pystac_client import Client
import planetary_computer

# NOT: Bu script arcpy GEREKTIRMEZ, STAC/pystac_client kutuphaneleri
# ArcGIS Pro'nun python ortaminda kurulu olmadigi icin ayri (afet_env) ortamda calisir.
# Cikti dosyalari sonraki adimda (24_ndvi_fuel_analysis.py, arcpy ortaminda) kullanilir.

workspace = r"C:\Users\PC\Desktop\projeler\FireImpact-GIS\data\Sentinel2_Raw"
os.makedirs(workspace, exist_ok=True)


def download_asset(asset, output_path):
    if os.path.exists(output_path):
        print(f"Zaten mevcut: {output_path}")
        return
    print(f"Indiriliyor -> {output_path}")
    r = requests.get(asset.href, stream=True)
    with open(output_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    print("Indirme tamamlandi!")


catalog = Client.open(
    "https://planetarycomputer.microsoft.com/api/stac/v1",
    modifier=planetary_computer.sign_inplace,
)

print("1. Kuzey karo (36SUG) icin yangin oncesi B04 (Kirmizi bant) araniyor...")
bbox_north = [31.3, 36.7, 31.6, 37.0]
search_pre_n = catalog.search(
    collections=["sentinel-2-l2a"], bbox=bbox_north,
    datetime="2021-07-01/2021-07-27", query={"eo:cloud_cover": {"lt": 10}},
)
items_n = list(search_pre_n.items())
best_n = sorted(items_n, key=lambda x: x.properties["eo:cloud_cover"])[0]
print(f"   Bulundu: {best_n.id} (Tarih: {best_n.datetime})")
download_asset(best_n.assets["B04"], os.path.join(workspace, "pre_fire_B04.tif"))

print("\n2. Guney karo (36SUF) icin yangin oncesi B04 araniyor...")
bbox_south = [31.3, 36.4, 31.6, 36.7]
search_pre_s = catalog.search(
    collections=["sentinel-2-l2a"], bbox=bbox_south, datetime="2021-07-19/2021-07-22",
)
items_s = list(search_pre_s.items())
same_pass_s = [i for i in items_s if i.properties.get("s2:mgrs_tile") == "36SUF" or "36SUF" in i.id]
same_pass_s = [i for i in same_pass_s if "20210720" in i.id or "2021-07-20" in i.datetime.strftime("%Y-%m-%d")]
if not same_pass_s:
    raise RuntimeError("Guney karo icin uygun goruntu bulunamadi!")
best_s = same_pass_s[0]
print(f"   Bulundu: {best_s.id}")
download_asset(best_s.assets["B04"], os.path.join(workspace, "pre_fire_south_B04.tif"))

print("\nTamamlandi! Simdi scripts/24_ndvi_fuel_analysis.py'i ArcGIS Pro python'uyla calistir.")
