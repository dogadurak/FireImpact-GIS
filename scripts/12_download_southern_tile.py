import os
import requests
from pystac_client import Client
import planetary_computer
import datetime

print("Microsoft Planetary Computer üzerinden Güney (T36SUF) Sentinel-2 verileri aranıyor...")

# The southern tile bbox
bbox_south = [31.3, 36.4, 31.6, 36.7]

catalog = Client.open(
    "https://planetarycomputer.microsoft.com/api/stac/v1",
    modifier=planetary_computer.sign_inplace,
)

out_dir = r"C:\Users\PC\Desktop\projeler\FireImpact-GIS\data\Sentinel2_Raw"
os.makedirs(out_dir, exist_ok=True)

def download_asset(asset, output_path):
    if os.path.exists(output_path):
        print(f"Zaten mevcut: {output_path}")
        return
    print(f"İndiriliyor -> {output_path}")
    response = requests.get(asset.href, stream=True)
    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    print("İndirme tamamlandı!")

# Pre-fire (July 20 2021) - Must match northern pass!
print("Yangın Öncesi Güney (Pre-fire South) uydusu aranıyor...")
search_pre = catalog.search(
    collections=["sentinel-2-l2a"],
    bbox=bbox_south,
    datetime="2021-07-19/2021-07-22",
)
items_pre = list(search_pre.items())
same_pass_pre = [i for i in items_pre if i.properties.get("grid:code", "").endswith("36SUF") or "36SUF" in i.id]
if not same_pass_pre:
    # try looking at mgrs property
    same_pass_pre = [i for i in items_pre if i.properties.get("s2:mgrs_tile") == "36SUF" or "36SUF" in i.id]

# Filter by date 2021-07-20
same_pass_pre = [i for i in same_pass_pre if "20210720" in i.id or "2021-07-20" in i.datetime.strftime("%Y-%m-%d")]

if same_pass_pre:
    best_pre = same_pass_pre[0]
    print(f"Bulundu: {best_pre.id}")
    download_asset(best_pre.assets["B08"], os.path.join(out_dir, "pre_fire_south_B08.tif"))
    download_asset(best_pre.assets["B12"], os.path.join(out_dir, "pre_fire_south_B12.tif"))
    download_asset(best_pre.assets["SCL"], os.path.join(out_dir, "pre_fire_south_SCL.tif"))
    download_asset(best_pre.assets["visual"], os.path.join(out_dir, "pre_fire_south_TCI.tif"))
else:
    print("Güney için uygun görüntü bulunamadı (Pre)!")

# Post-fire (August 29 2021) - Must match northern pass!
print("\nYangın Sonrası Güney (Post-fire South) uydusu aranıyor...")
search_post = catalog.search(
    collections=["sentinel-2-l2a"],
    bbox=bbox_south,
    datetime="2021-08-28/2021-08-30",
)
items_post = list(search_post.items())
same_pass_post = [i for i in items_post if i.properties.get("s2:mgrs_tile") == "36SUF" or "36SUF" in i.id]
same_pass_post = [i for i in same_pass_post if "20210829" in i.id or "2021-08-29" in i.datetime.strftime("%Y-%m-%d")]

if same_pass_post:
    best_post = same_pass_post[0]
    print(f"Bulundu: {best_post.id}")
    download_asset(best_post.assets["B08"], os.path.join(out_dir, "post_fire_south_B08.tif"))
    download_asset(best_post.assets["B12"], os.path.join(out_dir, "post_fire_south_B12.tif"))
    download_asset(best_post.assets["SCL"], os.path.join(out_dir, "post_fire_south_SCL.tif"))
    download_asset(best_post.assets["visual"], os.path.join(out_dir, "post_fire_south_TCI.tif"))
else:
    print("Güney için uygun görüntü bulunamadı (Post)!")

print("\nGüney verileri tamamlandı!")
